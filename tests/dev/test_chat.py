import importlib
import io
import json
from pathlib import Path
from urllib.error import HTTPError

import pytest
from azure.core.exceptions import ClientAuthenticationError


@pytest.fixture
def chat(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]))
    module = importlib.import_module("dev.chat")
    monkeypatch.setattr(module, "TOKEN", None)
    return module


@pytest.mark.parametrize("terminal", [True, False])
def test_stream_colors_and_plain_redirect(chat, monkeypatch, terminal):
    output = io.StringIO()
    monkeypatch.setattr(output, "isatty", lambda: terminal)
    monkeypatch.setattr(chat.sys, "stdout", output)
    reply = {
        "session_id": "session-1",
        "citations": [{"source": "policy.docx", "section": "Solicitud"}],
        "usage": {"prompt_tokens": 3226, "completion_tokens": 1186},
    }
    events = [
        ("tool_call", {"name": "lookup", "arguments": {"id": 1}}),
        ("tool_result", {"status": "ok", "content": "Encontrado"}),
        ("intent", {"intent": "data_query"}),
        ("delta", {"text": "Hola"}),
        ("delta", {"text": " mundo"}),
        ("end", reply),
    ]
    stream = io.BytesIO("".join(
        f"event: {name}\ndata: {json.dumps(data)}\n\n" for name, data in events
    ).encode())
    monkeypatch.setattr(chat.urllib.request, "urlopen", lambda *args, **kwargs: stream)
    elapsed = iter([12103, 12272])
    monkeypatch.setattr(chat, "milliseconds_since", lambda start: next(elapsed))

    assert chat.send("Consulta", None) == "session-1"
    text = output.getvalue()
    expected = [
        ("  → lookup(id=1)", chat.PURPLE),
        ("    resultado: Encontrado", chat.PURPLE),
        ("  Agente [data_query]: ", chat.CYAN),
        ("Hola", chat.CYAN),
        (" mundo", chat.CYAN),
        ("  Fuentes:", chat.YELLOW),
        ("   [1] policy.docx · Solicitud", chat.YELLOW),
        ("  (primer texto en 12103 ms, respuesta completa en 12272 ms, "
         "3226 tokens de entrada, 1186 de salida)", chat.ORANGE),
    ]
    for value, color in expected:
        assert (f"{color}{value}{chat.RESET}" if terminal else value) in text
    if not terminal:
        assert "\033[" not in text


@pytest.mark.parametrize("exit_error", [EOFError, KeyboardInterrupt])
def test_input_color_resets_on_exit(chat, monkeypatch, exit_error):
    output = io.StringIO()
    monkeypatch.setattr(output, "isatty", lambda: True)
    monkeypatch.setattr(chat.sys, "stdout", output)
    monkeypatch.setattr(chat.sys, "argv", ["chat.py"])
    monkeypatch.setattr(chat, "check_health", lambda: None)

    def interrupted_input(prompt):
        assert prompt == f"{chat.GREEN}Tú: "
        raise exit_error

    monkeypatch.setattr("builtins.input", interrupted_input)
    chat.main()
    assert output.getvalue().endswith(chat.RESET)


def test_single_query_is_green(chat, monkeypatch):
    output = io.StringIO()
    monkeypatch.setattr(output, "isatty", lambda: True)
    monkeypatch.setattr(chat.sys, "stdout", output)
    monkeypatch.setattr(chat.sys, "argv", ["chat.py", "Mi", "consulta"])
    monkeypatch.setattr(chat, "check_health", lambda: None)
    calls = []
    monkeypatch.setattr(chat, "send", lambda message, session_id: calls.append((message, session_id)))

    chat.main()

    assert output.getvalue() == f"{chat.GREEN}Tú: Mi consulta{chat.RESET}\n"
    assert calls == [("Mi consulta", None)]


def test_authenticated_health_stream_and_action(chat, monkeypatch, capsys):
    monkeypatch.setattr(chat, "AGENT_URL", "https://agent.example")
    monkeypatch.setattr(chat, "TOKEN", lambda: "token-prueba")
    monkeypatch.setattr("builtins.input", lambda prompt: "n")
    requests = []

    def urlopen(request, timeout):
        requests.append(request)
        if request.full_url.endswith("/health"):
            return io.BytesIO(b'{"status":"ok"}')
        if request.full_url.endswith("/chat/stream"):
            return io.BytesIO(b'event: end\ndata: {"session_id":"s","usage":{"prompt_tokens":0,"completion_tokens":0}}\n\n')
        return io.BytesIO(b'{"tools":[],"intent":"other","answer":"Listo"}')

    monkeypatch.setattr(chat.urllib.request, "urlopen", urlopen)
    chat.check_health()
    assert chat.send("Hola", None) == "s"
    chat.decide("s", {"id": "a", "name": "action", "arguments": {}})

    assert "Agente en https://agent.example: ok" in capsys.readouterr().out
    assert [request.get_header("Authorization") for request in requests] == ["Bearer token-prueba"] * 3


def test_local_health_without_token(chat, monkeypatch, capsys):
    def urlopen(request, timeout):
        assert request.get_header("Authorization") is None
        return io.BytesIO(b'{"status":"ok"}')

    monkeypatch.setattr(chat.urllib.request, "urlopen", urlopen)
    chat.check_health()
    assert ": ok" in capsys.readouterr().out


def test_health_timeout_is_explicit(chat, monkeypatch):
    def urlopen(request, timeout):
        raise TimeoutError("timeout")

    monkeypatch.setattr(chat.urllib.request, "urlopen", urlopen)
    with pytest.raises(SystemExit, match="no respondió a tiempo"):
        chat.check_health()


@pytest.mark.parametrize("status", [401, 403])
def test_health_reports_empty_auth_errors(chat, monkeypatch, capsys, status):
    def urlopen(request, timeout):
        raise HTTPError(request.full_url, status, "Forbidden", {}, io.BytesIO(b""))

    monkeypatch.setattr(chat.urllib.request, "urlopen", urlopen)
    with pytest.raises(SystemExit) as exc:
        chat.check_health()
    assert exc.value.code == 1
    assert f"Error {status}" in capsys.readouterr().out


def test_http_errors_preserve_json_detail(chat, monkeypatch, capsys):
    def urlopen(request, timeout):
        raise HTTPError(request.full_url, 422, "Invalid", {}, io.BytesIO(b'{"detail":"mensaje requerido"}'))

    monkeypatch.setattr(chat.urllib.request, "urlopen", urlopen)
    assert chat.send("Hola", None) is None
    assert "Error 422: mensaje requerido" in capsys.readouterr().out


def test_credential_failure_is_explicit(chat, monkeypatch):
    monkeypatch.setattr(chat, "AGENT_URL", "https://agent.example")

    def fail():
        raise ClientAuthenticationError(message="Credenciales no disponibles")

    monkeypatch.setattr(chat, "TOKEN", fail)
    with pytest.raises(SystemExit, match="az login"):
        chat.headers()


def test_token_requires_https(chat, monkeypatch):
    monkeypatch.setattr(chat, "AGENT_URL", "http://agent.example")
    monkeypatch.setattr(chat, "TOKEN", lambda: pytest.fail("No debe solicitar credenciales"))
    with pytest.raises(SystemExit, match="HTTPS"):
        chat.headers()
