"""Cliente de consola para conversar con el agente, sin pelear con las comillas ni las tildes de PowerShell.

uv run python dev/chat.py            conversación: escribe tus mensajes; "nueva" empieza otra sesión, "salir" termina
uv run python dev/chat.py "Hola"     un solo mensaje y termina

La respuesta aparece mientras el agente la escribe (POST /chat/stream, Server-Sent Events), y antes, cada tool que usa.
AGENT_URL cambia la dirección del agente (por defecto http://127.0.0.1:8000).
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from http.client import HTTPResponse

URL = os.environ.get("AGENT_URL", "http://127.0.0.1:8000").rstrip("/") + "/chat/stream"
TOOL_STATUS = {"ok": "resultado", "error": "error", "pending_approval": "NO SE EJECUTA, pendiente de aprobación"}
RESET = "\033[0m"
GREEN = "\033[92m"
CYAN = "\033[96m"
PURPLE = "\033[95m"
YELLOW = "\033[93m"
ORANGE = "\033[38;5;208m"


def colored(text: str, color: str) -> str:
    return f"{color}{text}{RESET}" if sys.stdout.isatty() else text


def send(message: str, session_id: str | None) -> str | None:
    """Envía el mensaje, muestra la respuesta mientras llega y devuelve el session_id para el siguiente turno."""
    body = json.dumps({"message": message, "session_id": session_id}).encode("utf-8")
    request = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    sent_at = time.perf_counter()
    try:
        response = urllib.request.urlopen(request, timeout=120)
    except urllib.error.HTTPError as error:  # falló antes de empezar a responder: llega como HTTP normal
        show_error(error.code, json.loads(error.read().decode("utf-8")))
        return None
    except urllib.error.URLError:
        sys.exit(f"No hay agente en {URL}. ¿Lo levantaste con uvicorn en otra terminal?")

    first_text_ms = None
    with response:
        for name, data in read_events(response):
            match name:
                case "tool_call":
                    arguments = ", ".join(f"{key}={value}" for key, value in data["arguments"].items())
                    print(colored(f"  → {data['name']}({arguments})", PURPLE), flush=True)
                case "tool_result":
                    print(colored(f"    {TOOL_STATUS[data['status']]}: {data['content'][:160]}", PURPLE), flush=True)
                case "intent":
                    print(colored(f"  Agente [{data['intent']}]: ", CYAN), end="", flush=True)
                case "delta":
                    first_text_ms = first_text_ms or milliseconds_since(sent_at)
                    print(colored(data["text"], CYAN), end="", flush=True)
                case "end":
                    print()
                    show_end(data, first_text_ms, milliseconds_since(sent_at))
                    return data["session_id"]
                case "error":
                    print()
                    show_error(200, data)
    return None


def read_events(response: HTTPResponse) -> Iterator[tuple[str, dict]]:
    """Lee los eventos a medida que llegan: cada uno es una línea "event: <nombre>" y una "data: <json>"."""
    name = ""
    for raw_line in response:
        line = raw_line.decode("utf-8").rstrip("\r\n")
        if line.startswith("event: "):
            name = line.removeprefix("event: ")
        elif line.startswith("data: "):
            yield name, json.loads(line.removeprefix("data: "))


def show_end(reply: dict, first_text_ms: int | None, total_ms: int) -> None:
    if citations := reply.get("citations"):
        print(colored("  Fuentes:", YELLOW))
        for number, citation in enumerate(citations, start=1):
            print(colored(f"   [{number}] {citation['source']} · {citation['section']}", YELLOW))
    usage = reply["usage"]
    first_text = f"primer texto en {first_text_ms} ms, " if first_text_ms else ""
    print(colored(f"  ({first_text}respuesta completa en {total_ms} ms, "
                  f"{usage['prompt_tokens']} tokens de entrada, {usage['completion_tokens']} de salida)", ORANGE))


def show_error(status: int, reply: dict) -> None:
    detail = reply.get("detail")
    if isinstance(detail, list):  # 422: FastAPI explica qué campo no pasó la validación
        detail = "; ".join(problem.get("msg", str(problem)) for problem in detail)
    kind = f" ({reply['error']})" if reply.get("error") else ""
    where = "a mitad de la respuesta" if status == 200 else str(status)
    print(f"  Error {where}{kind}: {detail}")


def milliseconds_since(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


def main() -> None:
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        print(colored(f"Tú: {message}", GREEN))
        send(message, None)
        return
    print('Conversación con el agente. Escribe "nueva" para otra sesión o "salir" para terminar.')
    session_id = None
    while True:
        try:
            try:
                message = input(f"{GREEN}Tú: " if sys.stdout.isatty() else "Tú: ")
            finally:
                if sys.stdout.isatty():
                    print(RESET, end="", flush=True)
        except (EOFError, KeyboardInterrupt):
            break
        if message.strip().lower() == "salir":
            break
        if message.strip().lower() == "nueva":
            session_id = None
            print("  (sesión nueva)")
            continue
        session_id = send(message, session_id) or session_id


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
