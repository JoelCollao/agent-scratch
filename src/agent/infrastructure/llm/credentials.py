from collections.abc import Callable

from azure.identity import AzureCliCredential, DefaultAzureCredential, get_bearer_token_provider
from pydantic import SecretStr

from agent.infrastructure.config.settings import AuthProvider

ENTRA_SCOPE = "https://cognitiveservices.azure.com/.default"

Credential = str | Callable[[], str]  # api key fija o proveedor de token renovable

# JP - CONVERSACIONAL -- 7 --Credenciales (solo si hay errores de autenticación): credentials.py
# build_credential: pon un breakpoint si tienes errores 502 con "token de Entra ID".
def build_credential(provider: AuthProvider, api_key: SecretStr) -> Credential:
    match provider:
        case AuthProvider.API_KEY:
            if not api_key.get_secret_value():
                raise RuntimeError("FOUNDRY_AUTH_PROVIDER=api_key requiere FOUNDRY_API_KEY.")
            return api_key.get_secret_value()
        case AuthProvider.ENTRA_ID:
            #az login en local, Managed Identity desplegado
            return get_bearer_token_provider(DefaultAzureCredential(), ENTRA_SCOPE)
            #return get_bearer_token_provider(
            #    AzureCliCredential(tenant_id="8a5bbed1-a0ce-4bf8-b532-842cfabb24cd"), #CON ESE CODIGO SOLO LEE EL TENANT QUE CORRESPONDE CON EL DefaultAzureCredential Busca credenciales y trata de ponerla pero fallan
            #    ENTRA_SCOPE,
            #)
