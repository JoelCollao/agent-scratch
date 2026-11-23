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

Despliegue en Azure con GitHub Actions: [devops/DESPLIEGUE.md](devops/DESPLIEGUE.md).

## En qué va

| Versión | Qué hace el agente | Estado |
|---|---|---|
| `main` | arquetipo: capas, contratos y `TODO` por sesión | ✅ |
| `t1-s1` | `/chat` con respuesta tipada contra el mock de Foundry | ✅ |
| `t1-s2` = `t1-v0.1` | historial por sesión, errores tipados, consumo por turno y Entra ID | ✅ |
| `t2-s3` | ingesta del corpus del dominio e índice local | ✅ |
| `t2-s4` | retrieval híbrido (Qdrant local o Azure AI Search) y RAG con citas en `/chat` | ✅ |
| `t2-s5` = `t2-v0.2` | golden set de 30 casos por dominio, juez (G-Eval o decision-1) y datos personales enmascarados | ✅ |
| `t3-*` → `t3-v0.3` | tools MCP, memoria y aprobación humana | ⏳ |
| `t4-*` → `t4-v0.4` | despliegue, trazas, evaluaciones y guardrails | ⏳ |
| `v1.0` | integración final | ⏳ |

Esta copia está en `t2-s5`. Para saber en qué versión está la tuya: `git describe --tags`.

## Requisitos

| Herramienta | Desde |
|---|---|
| Python 3.12, [uv](https://docs.astral.sh/uv/) y Git | la sesión 1 |
| Azure CLI y acceso a Microsoft Foundry (`gpt-5-mini`, `text-embedding-3-small`) | la sesión 2 |
| Azure AI Search (opcional en local: Qdrant) | la sesión 4 |
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

## Integración de un tag a una rama para empezar una sesión

### 1. Preparar la rama del equipo

Se empezó desde `main` actualizado. `origin` corresponde al repositorio del capitán y `upstream` al repositorio principal `https://github.com/NTTData-Academy/agent-scratch.git`.

```powershell
git fetch origin
git fetch upstream --tags --force
git switch -C equipo-12 t3-s7
```

Para publicar la rama del equipo se usó:

```powershell
git push origin equipo-12
```

Si la publicación es rechazada porque requiere reemplazar el historial remoto, la alternativa es:

```powershell
git push --force-with-lease origin equipo-12
```

**Precaución:** `fetch --tags --force` puede reemplazar tags locales y `switch -C` reposiciona la rama local `equipo-12` en el tag. `push --force-with-lease` puede reemplazar el historial remoto: coordínalo con el equipo y conserva cualquier trabajo necesario. El push normal se usa cuando Git permite la actualización, no simplemente porque no haya cambios locales.

### 2. Crear la rama de cada integrante

Cada integrante, también el capitán, crea su rama de sesión desde `equipo-NN` del repositorio del capitán:

```powershell
git fetch origin
git switch -c s7_AIE_<CÓDIGO> origin/equipo-NN
uv sync
uv run pytest
```

Reemplaza `<CÓDIGO>` y `NN` antes de ejecutar. En esta sesión se usó:

```powershell
git fetch origin
git switch -c s7_AIE_17JC origin/equipo-12
uv sync
uv run pytest
```

**Resultado obtenido:**

- Se creó `s7_AIE_17JC` desde `origin/equipo-12`, con seguimiento de esa rama remota.
- Se preparó `equipo-12` desde `t3-s7` y se publicó en `origin`; por eso la rama personal heredó el código del tag sin hacer un merge adicional.
- `uv sync` preparó las dependencias del laboratorio.
- `uv run pytest` terminó con **119 pruebas correctas y 5 omitidas en 36,77 segundos**.

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

Levantar la aplicación con datos de AI Search
Con SEARCH_ENDPOINT y SEARCH_INDEX configurados y el índice ya publicado, ejecuta en la terminal del servidor:

uv run --with truststore python -c "import truststore; truststore.inject_into_ssl(); import uvicorn; uvicorn.run('agent.infrastructure.bootstrap:create_app', factory=True)"

### Chat de consola

En otra terminal, ejecuta `uv run python dev/chat.py` (o `uv run python dev/chat.py "Hola"` para una sola consulta).
El cliente comprueba `/health` antes de conversar. Para un agente en Azure, configura `AGENT_URL` con su URL HTTPS
y `AGENT_SCOPE` con el scope de Entra ID terminado en `/.default`; `DefaultAzureCredential` puede usar `az login`.
La consulta aparece en verde, la respuesta y etiquetas como `[data_query]` en celeste, las tools en morado,
las fuentes RAG en amarillo y los tiempos y tokens en naranja. Los colores se desactivan al redirigir la salida.