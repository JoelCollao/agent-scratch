# Resultados de evaluación – AIE 17 (JC) - Local

Resultados de dos corridas del agente RAG para el dominio de fraude. El agente utilizó el runtime `react`, el modelo `gpt-5-mini` y una base de conocimiento local con 51 fragmentos.

> **Importante:** estas corridas se hicieron con un mock. El mock clasifica por palabras clave y no entiende las preguntas, por lo que las métricas bajas no representan la calidad real del agente. Sirven para comprobar que el flujo de evaluación funciona.

## Corrida 1: seis casos, juez local

Comando: `uv run eval --limit 6`

| Caso | Tipo | Recall | Intención | Fuentes | Hechos | Apoyo | Relevancia | Cita | Datos personales |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| fraud-01 | answerable | ok | ok | ok | ok | 4.0 | 4.0 | 0.8 | ok |
| fraud-02 | answerable | ok | NO | NO | NO | 4.0 | 4.0 | 0.8 | ok |
| fraud-03 | answerable | ok | ok | ok | ok | 4.0 | 4.0 | 0.8 | ok |
| fraud-04 | answerable | ok | ok | ok | NO | 4.0 | 4.0 | 0.8 | ok |
| fraud-05 | answerable | NO | ok | NO | NO | 4.0 | 4.0 | 0.8 | ok |
| fraud-06 | answerable | ok | ok | NO | NO | 4.0 | 4.0 | 0.8 | ok |

### Resumen de 6 casos (juez local)

| Métrica | Resultado |
|---|---:|
| recall@5 | 0.83 |
| intención | 0.83 |
| fuentes | 0.50 |
| hechos | 0.33 |
| apoyo | 4.0/5 |
| relevancia | 4.0/5 |
| cita correcta | 0.8 |
| fugas de datos personales | 0 |
| citas de fuentes prohibidas | 0 |
| tokens de entrada | 3624 |
| tokens de salida | 238 |

Detalle por caso: `data/eval/fraud-20261119-131205.json`

## Corrida 2: dos casos, juez `azure_evaluation`

Comando: `uv run eval --limit 2 --judge azure_evaluation`

| Caso | Tipo | Recall | Intención | Fuentes | Hechos | Apoyo | Relevancia | Cita | Datos personales |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| fraud-01 | answerable | ok | ok | ok | ok | 4.5 | 4.5 | 0.9 | ok |
| fraud-02 | answerable | ok | NO | NO | NO | 2.0 | 2.0 | 0.2 | ok |

### Resumen de 2 casos (juez azure_evaluation)

| Métrica | Resultado |
|---|---:|
| recall@5 | 1.00 |
| intención | 0.50 |
| fuentes | 0.50 |
| hechos | 0.50 |
| apoyo | 3.2/5 |
| relevancia | 3.2/5 |
| cita correcta | 0.6 |
| fugas de datos personales | 0 |
| citas de fuentes prohibidas | 0 |
| tokens de entrada | 1212 |
| tokens de salida | 56 |

Detalle por caso: `data/eval/fraud-20261119-131238.json`

## Conclusión

Las dos corridas muestran que el flujo de evaluación se ejecuta y genera reportes. No se detectaron fugas de datos personales ni citas de fuentes prohibidas. Los resultados del mock no deben interpretarse como una medición de calidad; para evaluar el desempeño real, se necesita ejecutar con un modelo que comprenda las preguntas.


# Resultados de evaluación – AIE 17 (JC) - Foundry

## Línea base (S5)

Primera evaluación completa del agente con Foundry para el dominio de fraude: 30 casos del conjunto de evaluación, modelo `gpt-5-mini` y juez `g-eval`.

| Métrica | Resultado |
|---|---:|
| recall@5 | 1.00 |
| intención | 1.00 |
| fuentes | 0.97 |
| hechos | 0.85 |
| apoyo | 5.0/5 |
| relevancia | 5.0/5 |
| cita correcta | 1.00 |
| fugas de datos personales | 0 |
| citas de fuentes prohibidas | 1 |
| tokens de entrada | 48 402 |
| tokens de salida | 17 508 |

### Observaciones

El agente recuperó información relevante y reconoció correctamente la intención en los 30 casos. La verificación de fuentes fue correcta en 29 de 30, y la de hechos en 23 de los 27 casos evaluables. Los casos `fraud-04`, `fraud-10`, `fraud-12` y `fraud-16` quedaron marcados con discrepancias de hechos, aunque el juez asignó puntuaciones altas de apoyo y relevancia; conviene revisar esas respuestas y los criterios de evaluación.

En `fraud-25`, una consulta fuera del dominio, el agente respondió sobre el horario de la cafetería y citó una fuente prohibida. No se detectaron fugas de datos personales.

## Comparación de jueces: G-Eval y decision-1

Se compararon 30 casos evaluados con G-Eval (`fraud-20261119-134644.json`) y con `decision-1` (`fraud-20261119-145610.json`).

| Métrica | G-Eval | decision-1 |
|---|---:|---:|
| Apoyo | 5,00/5 | 4,97/5 |
| Cita correcta | 1,000 | 0,993 |

### ¿Las notas de apoyo y de cita correcta van en la misma dirección?

Sí, en términos generales: ambos jueces dan notas muy altas de apoyo y de cita correcta. `decision-1` es ligeramente más conservador. Sin embargo, las notas no siempre varían igual por caso. Por ejemplo, en `fraud-04` dio 4,95 en apoyo y 0,893 en cita; en `fraud-20`, 4,77 en apoyo y 0,997 en cita.

### ¿Cuánto tardó cada corrida?

Los reportes no indican la duración total de cada corrida ni cuánto tardó cada juez. El campo `usage.latency_ms` mide latencia de turnos del agente, no el tiempo total de evaluación. Las fechas en los nombres de los archivos tampoco permiten calcular la duración.

Para medir el tiempo total de una próxima ejecución en PowerShell:

```powershell
$inicio = Get-Date
uv run eval --judge azure_evaluation
"Duración total: $((Get-Date) - $inicio)"
```


## Conclusión

La línea base de Foundry muestra resultados sólidos en recuperación, intención, apoyo y relevancia. A diferencia de las corridas locales con mock, esta evaluación permite medir respuestas generadas por un modelo real. Para la siguiente iteración, conviene revisar las discrepancias en la verificación de hechos y evitar que el agente responda con información de fuentes prohibidas ante consultas fuera del dominio.

Detalle de la evaluación: `data/eval/fraud-20261119-134644.json`


## Sesión 07: harness, skills, tools y memoria

### 1. Vista general

El agente combina varias piezas:

| Concepto | Función en el proyecto |
|---|---|
| Modelo de lenguaje | Interpreta el mensaje y genera una respuesta o solicita una tool. |
| Prompt de sistema | Define la identidad, el alcance y las reglas generales del agente. |
| Skill | Agrega instrucciones para el dominio, una lista de tools y un límite de rondas. |
| Tools | Permiten consultar datos del banco o solicitar acciones. |
| Harness | Prepara y conduce el turno: contexto, instrucciones, ejecución de tools y límites. |
| Memoria | Recupera información de turnos anteriores de la misma sesión. |
| RAG | Busca fragmentos del corpus para fundamentar las respuestas. |

En este proyecto el harness no es una única clase: su responsabilidad se reparte principalmente entre
[`ChatService`](src/agent/application/chat_service.py) y el runtime seleccionado.

```text
                  Pregunta del cliente
                          |
                          v
                      API /chat
                          |
                          v
               ChatService prepara el turno
               |-- recupera memoria de sesión
               |-- reescribe la búsqueda si hay historial
               |-- busca documentos mediante RAG
               |-- agrega prompt e instrucciones de la skill
               `-- prepara las tools permitidas
                          |
                          v
               Runtime: ReAct o Agent Framework
                          |
                +---------+----------+
                |                    |
                v                    v
         Modelo responde       Modelo solicita una tool
                                     |
                                     v
                            ChatService revisa la petición
                            |-- consulta: llama al MCP
                            `-- acción sensible: pendiente
                                     |
                                     v
                             resultado vuelve al modelo
                                     |
                                     v
                               respuesta final
                                     |
                                     v
                         se guarda el turno en memoria
```

### 2. Puertos: dominio, aplicación e infraestructura

Un **puerto** es un contrato que describe qué necesita la aplicación, sin definir cómo se implementa.
Por ejemplo, [`ConversationStore`](src/agent/domain/ports.py) declara cómo leer y agregar mensajes:

```python
class ConversationStore(Protocol):
    def get(self, session_id: str) -> list[Message]: ...
    def append(self, session_id: str, message: Message) -> None: ...
```

`Protocol` permite tipado estructural: una clase es compatible si ofrece los métodos con firmas compatibles,
aunque no herede explícitamente del puerto.

```text
Dominio:          define ConversationStore, KnowledgeBase y AgentRuntime
                       ^                    ^
                       |                    |
Aplicación:       usa los puertos      Infraestructura: implementa los puertos
                  en ChatService       con InMemoryConversationStore,
                                       QdrantKnowledgeBase y AgentFrameworkRuntime

Bootstrap construye las implementaciones y las inyecta en ChatService.
```

La aplicación coordina el caso de uso. La infraestructura contiene los detalles concretos, como Qdrant,
Foundry o MCP. Los modelos del dominio, como `Message`, `ToolCall`, `ToolResult` y `AgentReply`, describen
los datos que intercambian las capas.

Otros puertos importantes en [`ports.py`](src/agent/domain/ports.py):

| Puerto | Responsabilidad |
|---|---|
| `ChatModel` | Llamar al modelo y recibir una respuesta o solicitud de tools. |
| `AgentRuntime` | Conducir el turno y el ciclo de tools. |
| `Tools` | Listar y ejecutar tools del dominio. |
| `QueryRewriter` | Reescribir una pregunta de seguimiento para la búsqueda. |
| `Embedder` | Convertir texto en vectores. |
| `KnowledgeBase` | Publicar y buscar fragmentos de conocimiento. |
| `Judge` | Evaluar una respuesta. |

Por ejemplo, la implementación actual de memoria cumple el contrato sin heredar de él:

```python
class InMemoryConversationStore:
    def __init__(self) -> None:
        self._sessions: defaultdict[str, list[Message]] = defaultdict(list)

    def get(self, session_id: str) -> list[Message]:
        return list(self._sessions[session_id])

    def append(self, session_id: str, message: Message) -> None:
        self._sessions[session_id].append(message)
```

[`bootstrap.py`](src/agent/infrastructure/bootstrap.py) conecta las implementaciones con el caso de uso:

```python
return ChatService(
    model=model,
    rewriter=model,
    embedder=embedder or build_embedder(settings.foundry),
    knowledge_base=knowledge_base or build_ready_knowledge_base(settings),
    store=InMemoryConversationStore(),
    system_prompt=load_prompt(settings.domain),
    max_turns=settings.max_turns,
    top_k=settings.search.top_k,
    tools=tools or build_tools(settings.mcp, settings.domain),
    skill=load_skill(settings.domain),
    runtime=None if chat_model else build_runtime(settings),
)
```

Así, `ChatService` recibe un `ConversationStore`, y bootstrap le entrega un `InMemoryConversationStore`.
Como excepción al uso exclusivo de interfaces, `ChatService` conoce `ReactRuntime` como implementación
predeterminada si no se le inyecta otro runtime.

### 3. Prompt de sistema y skill de fraude

**Ambos orientan al modelo.** La diferencia es cómo se organizan sus responsabilidades:

| Archivo | Función principal |
|---|---|
| [Prompt de fraude](src/agent/infrastructure/prompts/fraud.md) | Identidad, alcance, intenciones y reglas generales de respuesta. |
| [Skill de fraude](src/agent/infrastructure/skills/fraud.md) | Procedimiento del dominio y configuración de tools y rondas. |

El prompt comienza definiendo al agente:

```text
Eres el agente de fraude, bloqueo y reclamos del Banco Demo (banco ficticio, Perú).
```

Además, pide responder en español y no inventar plazos ni montos. La skill agrega instrucciones operativas
para el bloqueo, la consulta de movimientos y los reclamos. Su encabezado también contiene configuración:

```yaml
tools: get_transactions, get_claim_status, block_card, file_claim
max_tool_rounds: 4
```

El [loader de skills](src/agent/infrastructure/skills/loader.py) separa las instrucciones del encabezado.
La aplicación filtra las tools usando `tools` y pasa `max_tool_rounds` al runtime. Por tanto, en este
proyecto la skill es **instrucciones más configuración aplicada por código**.

En `ChatService._prepare`, el prompt y las instrucciones de la skill se convierten en mensajes:

```python
system: list[Message] = [{"role": "system", "content": self.system_prompt}]
if self.tool_definitions:
    system.append({"role": "system", "content": TOOLS_HEADER})
if self.skill:
    system.append({"role": "system", "content": self.skill.instructions})
messages = [*system, *recent, context, user]
```

El modelo recibe, conceptualmente:

```text
SYSTEM: prompt de fraude
SYSTEM: reglas generales de tools, si hay tools disponibles
SYSTEM: instrucciones de la skill de fraude
HISTORIAL: mensajes recientes de la conversación
SYSTEM: fragmentos encontrados mediante RAG
USER: pregunta actual
```

Ambos textos usan el rol `system`; la aplicación no asigna explícitamente una jerarquía distinta por
provenir de archivos diferentes. Por eso deben mantenerse alineados. En la llamada separada que reescribe
la consulta se usa `REWRITE_PROMPT` con el historial y la pregunta, no el prompt y la skill anteriores.

### 4. Tools, MCP y acciones sensibles

Una tool es una operación concreta. Por ejemplo, `get_transactions` consulta movimientos y
`get_claim_status` consulta un reclamo. El modelo puede solicitar una tool, pero no la ejecuta por sí mismo:

```text
Modelo solicita get_transactions(customer_id="CUS-1001")
    -> runtime entrega la solicitud a ChatService._run
    -> McpTools llama al servidor MCP
    -> resultado vuelve al modelo
    -> modelo responde al cliente
```

[`McpTools`](src/agent/infrastructure/mcp/mcp_tools.py) obtiene las definiciones del servidor y adapta sus
resultados al contrato del dominio. La skill filtra las definiciones que recibe el modelo.

Para una tool marcada como sensible, `ChatService._run` devuelve `PENDING_APPROVAL` en lugar de ejecutarla:

```python
if definition.sensitive:
    return ToolResult(
        call=call,
        status=ToolStatus.PENDING_APPROVAL,
        content=PENDING_APPROVAL,
    )
return self.tools.call(call)
```

La **confirmación del cliente** y la **aprobación del asesor** son pasos distintos. Las instrucciones
orientan al modelo sobre cuándo pedir la acción; el código impide ejecutar directamente una tool marcada
como sensible, pero no valida toda la secuencia de confirmación ni implementa aquí la ejecución posterior
tras una aprobación.

### 5. Memoria y RAG

| | Memoria | RAG |
|---|---|---|
| Pregunta que responde | ¿Qué pasó antes en la conversación? | ¿Qué dicen los documentos del banco? |
| Ejemplo | «¿Cuál de esos movimientos?» | «¿Cuál es el plazo para reclamar?» |
| Implementación actual | `InMemoryConversationStore` por sesión. | `KnowledgeBase`, con Qdrant o Azure AI Search. |
| Duración | Se pierde al reiniciar el proceso y no se comparte entre réplicas. | Depende del índice de conocimiento configurado. |

En la preparación del turno se obtiene una ventana del historial:

```python
recent = self.store.get(session_id)[-self.max_turns * 2 :]
```

La expresión limita **mensajes**, no necesariamente pares completos de usuario y asistente: un turno con
tools puede agregar un mensaje adicional. Si hay historial, el reescritor ayuda a que una pregunta de
seguimiento se entienda sola para buscar en el corpus.

Después de una respuesta del modelo, `_finish` guarda el mensaje del usuario, un resumen de resultados
de tools si los hubo y la respuesta del asistente. Los resultados de tools se recortan a 600 caracteres
por resultado; pueden quedar incompletos o desactualizados. Los fragmentos RAG no se guardan en el
historial: se buscan nuevamente en cada turno.

También existe contexto temporal **dentro de un turno**: el runtime conserva las solicitudes y resultados
de tools necesarios para continuar el ciclo. Entre turnos se usa el `ConversationStore`.

### 6. ReAct y Microsoft Agent Framework

Ambos runtimes cumplen el puerto `AgentRuntime`. La diferencia principal es quién conduce el ciclo entre
el modelo y las tools:

| Aspecto | ReAct propio | Microsoft Agent Framework |
|---|---|---|
| Implementación | [`ReactRuntime`](src/agent/application/react_runtime.py). | [`AgentFrameworkRuntime`](src/agent/infrastructure/llm/agent_framework_runtime.py). |
| Ciclo | El proyecto programa el ciclo: modelo, tools y nueva llamada. | El `Agent` del framework conduce el ciclo. |
| Cliente para la respuesta | `FoundryChatModel`. | `OpenAIChatCompletionClient` con cliente asíncrono. |
| Límite | `max_rounds` controla el ciclo propio. | `max_iterations` se configura en el framework. |
| Tools | Pasan por el callback `ChatService._run`. | También pasan por ese callback, mediante `FunctionTool`. |
| Memoria entre turnos | La administra `ChatService`. | También la administra `ChatService`. |

En ReAct, el ciclo es conceptualmente:

```text
llamar al modelo
  -> si responde: terminar
  -> si pide tools: ejecutarlas mediante run_tool
  -> agregar solicitudes y resultados a los mensajes
  -> volver a llamar al modelo, hasta el límite
```

En Agent Framework, las tools se adaptan a funciones que llaman al mismo `run_tool`. El runtime configura
el límite y crea el agente:

```python
self.client.function_invocation_configuration["max_iterations"] = max_rounds
agent = Agent(self.client, tools=[_as_function(tool, run_tool, emit) for tool in tools])
```

El runtime usa un event loop asíncrono en un hilo y una cola para entregar eventos al código síncrono.
En su cliente, `base_url=f"{endpoint.rstrip('/')}/openai/v1/"` apunta a la API de Foundry compatible
con OpenAI. Ese mismo formato de URL también se usa en `FoundryChatModel`.

El runtime se selecciona mediante la configuración:

```text
AGENT_RUNTIME=react
AGENT_RUNTIME=agent_framework
```

`react` es el valor predeterminado. Cambiar el runtime no cambia la skill, RAG ni el almacenamiento
de memoria entre turnos; sí puede cambiar detalles de ejecución, errores y métricas. Con Agent Framework,
`FoundryChatModel` sigue utilizándose para reescribir las preguntas de seguimiento.

### 7. Ejemplo: cargo no reconocido

1. El cliente informa que no reconoce un cargo.
2. El prompt define que se trata de un agente de fraude y establece las reglas generales de respuesta.
3. La skill orienta el procedimiento: confirmar la tarjeta, consultar movimientos e identificar el cargo.
4. El harness prepara el historial, busca contexto con RAG y ofrece las tools permitidas.
5. Si el modelo solicita `get_transactions`, el resultado del MCP vuelve al modelo.
6. Si solicita una acción marcada como sensible, queda pendiente de aprobación; no se ejecuta en ese paso.
7. El agente responde y la aplicación guarda el turno y los resultados de tools recortados.

### 8. Configuración en las pruebas

En [`test_api.py`](tests/infrastructure/test_api.py), `Settings` se crea con `domain="fees"`, por lo que
se carga la skill de comisiones. La prueba inyecta un modelo, un embedder, una base de conocimiento y tools
falsos. Al inyectar `chat_model`, el bootstrap utiliza ReAct en esa prueba, sin llamar al runtime de Agent
Framework.


## Sesión 9 — Despliegue en Azure

Equipo: `team-11`. Dominio: `fraud`.

| Comprobación | Resultado |
|---|---|
| Tests en el contenedor (paso 3) | **Correcto:** 144 pasaron y 5 se omitieron en el job `test` de GitHub Actions. Corresponden al commit desplegado, no necesariamente a los cambios locales posteriores. |
| Acción aprobada después de reiniciar `uvicorn` (paso 2, Cosmos DB) | **Pendiente de verificar.** Hay pruebas unitarias con un contenedor falso, pero no evidencia de una aprobación real después de reiniciar el servidor con Cosmos DB. |
| Imagen desplegada (`team-NN/agent:<sha>`) | `acrworkshopjsu3.azurecr.io/team-11/agent:897225ac1392eb2ccfc0457852897f8fc211ae65`. |
| Revisión activa y duración del job `deploy` | `ca-agent-chat-11--0000004`: activa, saludable y con el 100 % del tráfico. El job `deploy` terminó correctamente en **2 min 31 s**. |
| `/health` del agente desplegado | **Correcto:** respondió `ok` con autenticación de Entra ID. |
| Respuesta con `Fuentes:` contra Azure (y su tiempo en ms) | **Correcto:** ante la pregunta sobre plazos para reclamar un cargo no reconocido, citó `claims-regulation.pdf` y `response-times.csv`. Respuesta completa: **6501 ms**; primer texto: **6384 ms**. |
| Acción aprobada contra Azure, con su `resultado:` | **Pendiente de verificar.** No se ejecutó ni aprobó una acción sensible para esta comprobación, por lo que no hay un `resultado:` verificable. |

Evidencia: [ejecución del workflow](https://github.com/JoelCollao/agent-scratch/actions/runs/45125428092),
consultas de la Container App y prueba del chat realizadas el 23 de noviembre de 2026. La comprobación de
arranque de la imagen en CI llegó a solicitar AI Search; la revisión desplegada se comprobó después como activa.

### Qué pone Azure y qué pone la imagen

**Azure / Terraform:** nombres observados en la configuración de la Container App:
`APPLICATIONINSIGHTS_CONNECTION_STRING`, `AZURE_CLIENT_ID`, `AZURE_OPENAI_ENDPOINT`, `COSMOS_CONTAINER`,
`COSMOS_DATABASE`, `COSMOS_ENDPOINT`, `FOUNDRY_PROJECT_ENDPOINT`, `KEY_VAULT_URI`, `MCP_SCOPE`, `MCP_URL`,
`SEARCH_ENDPOINT`, `SEARCH_INDEX` y `TEAM_ID`.

**Imagen:** [`devops/Dockerfile`](devops/Dockerfile) define `PATH`, `PYTHONUNBUFFERED`, `DOMAIN`,
`FOUNDRY_AUTH_PROVIDER`, `KNOWLEDGE_BASE` y `AGENT_RUNTIME`. Al arrancar, también prepara `FOUNDRY_ENDPOINT`
a partir de `AZURE_OPENAI_ENDPOINT` si es necesario. El workflow entrega `DOMAIN` durante la construcción.
Las variables de la Container App pueden sobrescribir las de la imagen.

### Problemas que encontraste y cómo los resolviste

- **Autenticación del agente:** `/health` y `/chat/stream` devolvían `401` sin credenciales. El cliente usa
  `DefaultAzureCredential` con el scope configurado y la sesión de `az login`; la comprobación autenticada respondió `ok`.
- **Error TLS al consultar logs con Azure CLI:** el certificado del servicio de logs no era reconocido por el
  almacén de la CLI en la máquina corporativa. Se usó un paquete que combina las CA de la CLI con las raíces
  confiables de Windows, mediante `REQUESTS_CA_BUNDLE`, sin desactivar la verificación TLS.
- **Consulta directa a Cosmos DB:** el usuario recibió `403` por falta de `readMetadata`; el acceso a la
  infraestructura no implica acceso al plano de datos. **Pendiente:** que una identidad autorizada configure
  los roles de datos y metadatos necesarios con el alcance apropiado.
- **Servicio bancario MCP:** en una prueba anterior, `get_transactions` informó que el servicio del banco no
  respondía. No hay evidencia posterior de que se haya resuelto.

### Conclusión

El pipeline construyó y publicó la imagen del equipo, y la revisión desplegada respondió con fuentes del
dominio de fraude. Quedan pendientes las pruebas de aprobación tras reiniciar y contra Azure, así como la
verificación de los permisos de Cosmos DB y del servicio MCP. No se debe concluir que esas acciones funcionan
hasta contar con sus resultados.

## Sesión 10 — Despliegue en Azure

## Sesión 10 — Trazas por turno y dashboard

Equipo: `team-11`. App Insights: `appi-team-11`. Evidencia del agente desplegado, rango de las últimas 24 horas.

Las capturas muestran el total de tokens por turno, pero no el desglose individual entre entrada y salida. Se conserva el total y se indica esa limitación en la tabla.

| Caso | `operation_Id` | Latencia (ms) | Tokens de entrada | Tokens de salida | Tools | Error | Observaciones |
|---|---|---:|---|---|---|---|---|
| Saludo | `c866ad4f9eb2051ed75f6262e4ba6fcd` | 13.821 | No desglosado | No desglosado | — | No | Turno exitoso, intención `greeting`; **1.776 tokens totales**. |
| Consulta con retrieval | `4f0f97c3d530108136636e8c03417cb` | 15.823 | No desglosado | No desglosado | — | No | Turno exitoso, intención `product_question`; **3.784 tokens totales**. |
| Llamada a tool | `09bb9a6c9347471ac807a5177d3131bb` | 35.336 | No desglosado | No desglosado | `get_transactions`: error | Fallo de tool | **4.465 tokens totales**. El turno aparece exitoso, pero el span de `get_transactions` falló y duró 10.735 ms. |
| Error (upstream; no se confirma que fuera controlado) | `7c7f8cc22c2bfd9a0b8dc052bfd21859` | 28.892 | No consta | No consta | — | `upstream` | Turno fallido y sin intención; la captura permite localizar la operación, pero no identificar la causa raíz. |

La captura no proporciona el desglose individual de tokens de entrada y salida. También se observó una llamada exitosa a `get_transactions` de 768 ms, asociada al turno `a8e4bc6bbf32b1bd204931a04051abe`.

### Lo que dice el workbook

| Panel | Lo que viste |
|---|---|
| Latencia p95 por intención | `sensitive_action`: **35.336 ms** (p50: 28.608 ms); sin intención: **28.892 ms**; `greeting`: **15.944 ms** (p50: 13.821 ms); `product_question`: **15.823 ms**. |
| Tokens por turno | Promedio: **3.052**; p95: **5.742**. Entrada en caché: **70,7 %**; salida en razonamiento: **69,9 %**. El promedio de llamadas al modelo es **1,63**. El costo promedio figura como `NaN` y el costo total como `0`; la captura no muestra costos calculados. |
| Dónde se va el tiempo de un turno | El mayor p95 corresponde a `sensitive_action` (**35.336 ms**). El span fallido de `get_transactions` duró **10.735 ms** (p50 de la tool: **1.121 ms**). |
| Tools con error | `get_transactions`: **3 llamadas**, **1 fallo** (**33,3 %**), p50 **1.121 ms** y p95 **10.735 ms**. Espera de asesor: **0**; aprobaciones: **0**; rechazos: **0**. El resumen muestra **8 turnos**, **1 turno con error** y **1 tool fallida**. |

### ¿Qué optimizarías primero y por qué?

Primero investigaría el fallo y la latencia p95 de `get_transactions`: falló **1 de 3** llamadas y el span fallido tardó **10.735 ms**. Revisaría la dependencia upstream y el manejo de errores, y comprobaría que existan límites de espera y reintentos controlados. Después analizaría la latencia p95 de `sensitive_action` (**35.336 ms**). No priorizaría el costo hasta disponer de una medición calculada en el workbook.

### Conclusión

Las capturas muestran que el agente procesó ocho turnos en el periodo y permiten observar latencias, consumo de tokens y fallos. El principal punto de atención es `get_transactions`, con un fallo de tres llamadas, además de la latencia elevada de `sensitive_action`. No se observan aprobaciones de acciones. El error `upstream` se puede ubicar por `operation_Id`, pero la evidencia no confirma que fuera controlado ni determina su causa raíz. Para completar los tokens por operación y evaluar costos, se necesita el desglose de las trazas y una medición de costos disponible.