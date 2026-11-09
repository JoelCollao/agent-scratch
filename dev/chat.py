"""Cliente de consola para conversar con el agente, sin pelear con las comillas ni las tildes de PowerShell.

uv run python dev/chat.py            conversación: escribe tus mensajes; "nueva" empieza otra sesión, "salir" termina
uv run python dev/chat.py "Hola"     un solo mensaje y termina

AGENT_URL cambia la dirección del agente (por defecto http://127.0.0.1:8000).
En terminal, el usuario aparece en cyan y el agente en verde; al redirigir la salida no se usan colores.
La latencia aparece en amarillo, los tokens de entrada en naranja y los de salida en morado claro.
"""

import json
import os
import sys
import urllib.error
import urllib.request

URL = os.environ.get("AGENT_URL", "http://127.0.0.1:8000").rstrip("/") + "/chat"
CYAN = "\033[96m" if sys.stdout.isatty() else ""
GREEN = "\033[92m" if sys.stdout.isatty() else ""
YELLOW = "\033[93m" if sys.stdout.isatty() else ""
ORANGE = "\033[38;2;255;165;0m" if sys.stdout.isatty() else ""
LIGHT_PURPLE = "\033[38;2;190;150;255m" if sys.stdout.isatty() else ""
RESET = "\033[0m" if sys.stdout.isatty() else ""


def send(message: str, session_id: str | None) -> tuple[int, dict]:
    body = json.dumps({"message": message, "session_id": session_id}).encode("utf-8")
    request = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))
    except urllib.error.URLError:
        sys.exit(f"No hay agente en {URL}. ¿Lo levantaste con uvicorn en otra terminal?")


def show(status: int, reply: dict) -> str | None: #JP-FLUJO-CONVERSACION CHAT --> 1 Cliente: aquí lees tu mensaje con input
    """Imprime la respuesta y devuelve el session_id para el siguiente turno."""
    if status == 200:
        print(f"{GREEN}  Agente [{reply['intent']}]: {reply['answer']}{RESET}")
        if usage := reply.get("usage"):
            print(
                f"  ({YELLOW}{usage['latency_ms']} ms{RESET}, "
                f"{ORANGE}{usage['prompt_tokens']} tokens de entrada{RESET}, "
                f"{LIGHT_PURPLE}{usage['completion_tokens']} de salida{RESET})"
            ) #JP-SE MUESTRA LO QUE USAGE CAPTURO latencia , token entrada y token de salida
        return reply["session_id"]
    detail = reply.get("detail")
    if isinstance(detail, list):  # 422: FastAPI explica qué campo no pasó la validación
        detail = "; ".join(problem.get("msg", str(problem)) for problem in detail)
    kind = f" ({reply['error']})" if reply.get("error") else ""
    print(f"  Error {status}{kind}: {detail}")
    return None


def main() -> None:
    if len(sys.argv) > 1:
        show(*send(" ".join(sys.argv[1:]), None))
        return
    print('Conversación con el agente. Escribe "nueva" para otra sesión o "salir" para terminar.')
    session_id = None
    while True:
        try:
            try:
                print(CYAN, end="", flush=True)
                message = input("Tú: ")
            finally:
                print(RESET, end="", flush=True)
        except (EOFError, KeyboardInterrupt):
            break
        if message.strip().lower() == "salir":
            break
        if message.strip().lower() == "nueva":
            session_id = None
            print("  (sesión nueva)")
            continue
        session_id = show(*send(message, session_id)) or session_id


if __name__ == "__main__":
    main()
