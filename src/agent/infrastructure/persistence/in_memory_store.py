from collections import defaultdict

from agent.domain.models import Message, ToolCall

#JP - 1. Dónde se guarda (almacén en memoria)
#in_memory_store.py guarda un diccionario _sessions que asocia cada session_id con su lista de mensajes:

class InMemoryConversationStore: #JP-S2 -- CONVERSACIONAL -- 5 --Almacén de memoria: in_memory_store.py get y append: útiles para inspeccionar el diccionario _sessions y confirmar que el session_id coincide entre turno
    """Implementa el puerto ConversationStore en memoria."""

    # ponytail: se pierde al reiniciar y no escala a varias réplicas; Cosmos DB en T4
    def __init__(self) -> None:
        self._sessions: defaultdict[str, list[Message]] = defaultdict(list)
        self._pending: dict[str, ToolCall] = {}

    def get(self, session_id: str) -> list[Message]: #JP-DEVUELVE UNA COPIA DE LOS MENSAJES DE ESA SESION
        return list(self._sessions[session_id])

    def append(self, session_id: str, message: Message) -> None: #JP-AGREGA UN MENSAJE AL FINAL
        self._sessions[session_id].append(message)

    def pending(self, session_id: str) -> ToolCall | None:
        return self._pending.get(session_id)

    def set_pending(self, session_id: str, call: ToolCall | None) -> None:
        if call is None:
            self._pending.pop(session_id, None)
        else:
            self._pending[session_id] = call