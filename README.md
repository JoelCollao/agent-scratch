# agent-scratch

Agente conversacional bancario del **Banco Demo** (ficticio), construido paso a paso en el Workshop IA Engineers.
Cada equipo lo adapta a su dominio y lo hace crecer sesión a sesión hasta la v1.0.

## Objetivo

Un agente que atiende a los clientes del banco por consola y por API:

- **Conversa (T1):** entiende la intención del cliente y responde con un contrato tipado, con memoria por sesión.
- **Sabe (T2):** responde con el conocimiento del banco (RAG sobre el corpus de su dominio) y cita sus fuentes.
- **Actúa (T3):** consulta datos con tools MCP y ejecuta la acción sensible de su dominio solo con aprobación humana.
- **Opera (T4):** desplegado en Azure, observable, evaluado y protegido.

Dominios: `fraud`, `fees`, `cards`, `loans` y `support` (variable `DOMAIN`).

## En qué va

| Versión | Qué hace el agente | Estado |
|---|---|---|
| `main` | arquetipo: capas, contratos y `TODO` por sesión | ✅ |
| `t1-s1` | `/chat` con respuesta tipada contra el mock de Foundry | ✅ |
| `t1-s2` = `t1-v0.1` | historial por sesión, errores tipados, consumo por turno y Entra ID | ✅ |
| `t2-s3` | ingesta del corpus del dominio e índice local | ⏳ |
| `t2-s4` | retrieval híbrido y RAG con citas en `/chat` | ⏳ |
| `t2-s5` = `t2-v0.2` | evaluación del RAG y Azure AI Search | ⏳ |
| `t3-*` → `t3-v0.3` | tools MCP, memoria y aprobación humana | ⏳ |
| `t4-*` → `t4-v0.4` | despliegue, trazas, evaluaciones y guardrails | ⏳ |
| `v1.0` | integración final | ⏳ |

Esta copia está en `t1-s2` = `t1-v0.1`. Para saber en qué versión está la tuya: `git describe --tags`.

## Requisitos

| Herramienta | Desde |
|---|---|
| Python 3.12, [uv](https://docs.astral.sh/uv/) y Git | la sesión 1 |
| Azure CLI y acceso a Microsoft Foundry (`gpt-5-mini`, `text-embedding-3-small`) | la sesión 2 |
| Azure AI Search | la sesión 5 |
| Docker | el tema 4 |

## Levantarlo

```bash
copy .env.example .env
uv sync
uv run pytest
uv run python dev/mock_foundry.py
uv run uvicorn agent.infrastructure.bootstrap:create_app --factory
uv run python dev/chat.py
```

El mock de Foundry, el agente y el chat corren cada uno en su propia terminal. `.env.example` apunta al mock, así que no hace falta Azure.

El paso a paso de cada sesión (configuración, ejecución, pruebas y problemas frecuentes) está en el repo de labs del workshop.

## Problemas de certificados con Azure AI Search

Si aparece `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`, Python puede no reconocer un certificado que Windows sí considera confiable. En ese caso, usa `truststore` para consultar los certificados de Windows sin desactivar la validación HTTPS.

Si configuraste `REQUESTS_CA_BUNDLE` con una ruta inexistente, elimina esa variable en la terminal donde ejecutarás los comandos:

```powershell
Remove-Item Env:REQUESTS_CA_BUNDLE -ErrorAction SilentlyContinue
```

### Problemas al publicar en AI Search

Configura `SEARCH_ENDPOINT` y `SEARCH_INDEX` en `.env` con los valores de tu servicio. Necesitas una sesión de Azure CLI con permisos sobre el índice; si aún no iniciaste sesión, ejecuta `az login`.

Para publicar los chunks previamente generados con `uv run ingest build`, usando la confianza de Windows:

```powershell
uv run --with truststore python -c "import truststore; truststore.inject_into_ssl(); from agent.infrastructure.ingestion.cli import main; main()" publish --target azure_search
```

### Levantar la aplicación con datos de AI Search

Con `SEARCH_ENDPOINT` y `SEARCH_INDEX` configurados y el índice ya publicado, ejecuta en la terminal del servidor:

```powershell
$env:KNOWLEDGE_BASE = "azure_search"
uv run --with truststore python -c "import truststore; truststore.inject_into_ssl(); import uvicorn; uvicorn.run('agent.infrastructure.bootstrap:create_app', factory=True)"
```

Al iniciar, la aplicación consulta Azure AI Search para comprobar que el índice tiene documentos. Un error de certificado en esa consulta impide el arranque.

**Importante:** `truststore` se aplica solamente al proceso iniciado con cada comando. Usarlo al publicar no lo activa para el servidor. Estos comandos no modifican el código ni las dependencias declaradas del proyecto; `uv` proporciona `truststore` para la ejecución.

Si el error persiste, será necesario revisar la cadena de certificados y la configuración de red. No desactives la verificación SSL.

## Arquitectura

```
src/agent/
├── domain/          contratos y puertos; no importa nada externo
├── application/     casos de uso; solo conocen los puertos
└── infrastructure/  API, Foundry, búsqueda, persistencia, configuración y bootstrap
dev/                 herramientas locales: mock de Foundry y cliente de consola
devops/              contenedor y compose
```

Las dependencias van `infrastructure → application → domain`, nunca al revés.

-- Subida cambios
git status
git diff                  # Revisa los cambios
git add .
git diff --cached         # Revisa lo que vas a guardar
git commit -m "feat: sesión 2 - historial, errores tipados y usage contra Foundry"
git push