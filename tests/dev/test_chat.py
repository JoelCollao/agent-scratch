import importlib
import io
import json
from pathlib import Path

import pytest


@pytest.fixture
def chat(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2]))
    return importlib.import_module("dev.chat")


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
    calls = []
    monkeypatch.setattr(chat, "send", lambda message, session_id: calls.append((message, session_id)))

    chat.main()

    assert output.getvalue() == f"{chat.GREEN}Tú: Mi consulta{chat.RESET}\n"
    assert calls == [("Mi consulta", None)]
