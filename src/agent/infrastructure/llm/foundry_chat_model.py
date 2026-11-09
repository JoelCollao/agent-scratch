import logging
import time

from azure.core.exceptions import ClientAuthenticationError
from openai import (
    APIError,
    APITimeoutError,
    ContentFilterFinishReasonError,
    LengthFinishReasonError,
    OpenAI,
    RateLimitError,
)
from pydantic import ValidationError

from agent.domain.errors import AgentError, ErrorKind
from agent.domain.models import AgentReply, Message, ModelResult, Usage
from agent.infrastructure.llm.credentials import Credential

log = logging.getLogger(__name__)

#JP-S2- CONVERSACION - 6 - Llamada al modelo: foundry_chat_model.py
#Método complete(messages): en la línea de chat.completions.parse(...) 
#ves el request real. Luego revisa completion.choices[0].message.parsed para ver la respuesta ya validada y el objeto usage.
class FoundryChatModel:
    """Implementa el puerto ChatModel contra Microsoft Foundry (API v1 compatible con OpenAI)."""

    def __init__(
        self,
        endpoint: str,
        credential: Credential,
        deployment: str,
        timeout_s: float,
        max_retries: int,
    ) -> None:
        # el SDK reintenta con backoff timeouts, 429 y 5xx; AgentError llega tras agotar reintentos
        #donde se configura el cliente que hace los reintentos:
        self.client = OpenAI(
            base_url=f"{endpoint.rstrip('/')}/openai/v1/",
            api_key=credential,
            timeout=timeout_s,
            max_retries=max_retries, #JP El comportamiento viene del SDK de OpenAI-le indica cuántos reintentos hacer.
        )
        self.deployment = deployment

    def complete(self, messages: list[Message]) -> ModelResult:
        log.info("messages enviados al modelo: %s", messages)
        start = time.perf_counter()
        #JP
        try:
            completion = self.client.chat.completions.parse(
                model=self.deployment, messages=messages, response_format=AgentReply
            )
        except APITimeoutError as error:
            raise AgentError(ErrorKind.TIMEOUT, "Foundry no respondió a tiempo") from error
        except RateLimitError as error:
            raise AgentError(ErrorKind.RATE_LIMIT, "Foundry limitó las solicitudes (429)") from error
        except LengthFinishReasonError as error:
            raise AgentError(ErrorKind.INVALID_OUTPUT, "respuesta cortada por límite de tokens") from error
        except ContentFilterFinishReasonError as error:
            raise AgentError(ErrorKind.INVALID_OUTPUT, "respuesta bloqueada por el filtro de contenido") from error
        except ValidationError as error:
            raise AgentError(ErrorKind.INVALID_OUTPUT, "el modelo no devolvió el contrato esperado") from error
        except ClientAuthenticationError as error:
            raise AgentError(ErrorKind.UPSTREAM, "no se pudo obtener token de Entra ID (¿hiciste az login?)") from error
        except APIError as error:
            raise AgentError(ErrorKind.UPSTREAM, f"error de Foundry: {type(error).__name__}") from error

        message = completion.choices[0].message
        if message.parsed is None:
            raise AgentError(ErrorKind.INVALID_OUTPUT, f"el modelo no devolvió el contrato: {message.refusal or 'vacío'}")

        #JP-VER LA INTENCION QUE LLEGA DEL PROMPT DEL CLIENTE
        log.info("intencion detectada=%s | mensaje del cliente=%r", message.parsed.intent, messages[-1]["content"])
        
        tokens = completion.usage
        
        #JP-usage es el registro de consumo de una llamada al modelo: cuántos tokens usó, cuánto tardó y qué modelo respondió. Viaja desde Foundry hasta tu cliente en chat.py.
        usage = Usage(
            models=[completion.model or self.deployment],
            llm_calls=1,
            latency_ms=int((time.perf_counter() - start) * 1000),
            prompt_tokens=tokens.prompt_tokens if tokens else 0,
            completion_tokens=tokens.completion_tokens if tokens else 0,
        )
        log.info("llm %s", usage.model_dump())
        return ModelResult(reply=message.parsed, usage=usage) #JP - Se empaqueta
