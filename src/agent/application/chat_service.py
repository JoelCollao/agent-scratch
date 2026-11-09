from agent.domain.models import AgentTurn, Message
from agent.domain.ports import ChatModel, ConversationStore


class ChatService:
    """Caso de uso: resolver un turno de conversación. Solo conoce puertos, nunca infraestructura."""

    def __init__(self, model: ChatModel, store: ConversationStore, system_prompt: str, max_turns: int) -> None:
        self.model = model
        self.store = store
        self.system_prompt = system_prompt
        self.max_turns = max_turns

    #JP-CONVERSACION - 4 - Caso de uso (orquestación y memoria): chat_service.py
    def handle(self, session_id: str, message: str) -> AgentTurn: #Dónde se lee y se escribe en cada turno
                                                                  #En chat_service.py, el método handle:
        user: Message = {"role": "user", "content": message}
        recent = self.store.get(session_id)[-self.max_turns * 2 :] #trae el historial y se queda solo con los últimos max_turns * 2 mensajes (con max_turns=10, son 20). | es el historial antes de la llamada;
        result = self.model.complete([{"role": "system", "content": self.system_prompt}, *recent, user]) #envía al modelo el prompt del sistema, el historial y el mensaje nuevo, ves exactamente qué mensajes se envían al modelo;
        # se guarda solo si el modelo respondió: un error no deja turnos a medias
        #Después de que el modelo responde, guarda el mensaje del usuario y la respuesta del asistente con store.append. Si el modelo falla, no guarda nada.
        self.store.append(session_id, user)
        self.store.append(session_id, {"role": "assistant", "content": result.reply.answer}) #ves cuándo se guarda la memoria.
        return AgentTurn(reply=result.reply, usage=result.usage)
