"""Contrato HTTP del agente. Solo crece con campos opcionales: T2 citations, T3 pending_action, T4 trace_id."""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, StringConstraints

from agent.domain.errors import ErrorKind
from agent.domain.models import Intent, Usage

UserMessage = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class ChatRequest(BaseModel): #JP Validación de entrada: schemas.py - 3 -  puedes ver cómo Pydantic valida message y session_id antes de llegar a chat.
    session_id: UUID | None = None
    message: UserMessage


class ChatResponse(BaseModel): #JP - Estructura del chat con usage y pydantic
    #LO AGREGE PORQUE CUANDO LEVANTE LA APLICACION SIN AZ LOGIN ME RESPONDE EL AGENTE PERO ME SALI UN ERROR  return reply["session_id"]
    #Pero ChatResponse no declara session_id, por lo que el JSON no lo contiene.
    #Autenticación y modelo → respuesta exitosa
    #API → JSON sin session_id
    #Cliente → imprime respuesta → busca session_id → KeyError
    session_id: UUID #JP
    intent: Intent
    answer: str
    usage: Usage


class ErrorResponse(BaseModel):
    error: ErrorKind
    detail: str
