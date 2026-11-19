# Aprendizaje S4: Búsqueda híbrida, top-k, reranking y Azure AI Search

Guía de los cambios de la sesión 4: qué cambió en el código, por qué cambió y cómo se conecta con lo visto en [Aprendizaje_S2.md](Aprendizaje_S2.md) (el agente conversacional) y [Aprendizaje_S3.md](Aprendizaje_S3.md) (la ingesta: loaders, chunker, embeddings y Qdrant).

> Las etiquetas `#JP-S4` en el código son comentarios personales que marcan los puntos de esta sesión.

## 1. De dónde venimos

| Sesión | Qué construimos | Pregunta que respondía |
|---|---|---|
| S2 | `ChatService`, memoria por `session_id`, `AgentReply` con `intent`, `Usage`, errores HTTP | ¿Cómo conversa el agente? |
| S3 | Loaders → Markdown → chunker → embeddings → Qdrant (`publish`, `count`) | ¿Cómo guardamos el conocimiento? |
| **S4** | `search` híbrida, `top_k`, vigencia, reescritura de la pregunta, adaptador de Azure AI Search | **¿Cómo encontramos el conocimiento correcto para responder?** |

En S3 el índice solo sabía **guardar** (`publish`) y **contar** (`count`). Ahora también sabe **buscar** (`search`). Es la pieza que falta para el RAG: el modelo de S2 podrá responder con fragmentos del corpus en vez de responder de memoria.

## 2. Cambios en el código y por qué

### 2.1 El puerto `KnowledgeBase` ahora busca

En [ports.py](src/agent/domain/ports.py):

```python
def search(self, text: str, vector: list[float], top_k: int) -> list[SearchHit]:
    """Los top_k chunks vigentes más relevantes para la pregunta, del más al menos relevante."""
```

- **Por qué recibe `text` y `vector` a la vez:** la búsqueda híbrida usa los dos. El vector sirve para buscar por **significado** y el texto para buscar por **palabras exactas**.
- **Por qué devuelve `SearchHit`:** en [knowledge.py](src/agent/domain/knowledge.py), `SearchHit` es el `Chunk` más su `score`. Con eso se sabe qué tan relevante fue cada resultado.
- **Relación con S3:** sigue siendo arquitectura de puertos y adaptadores. El dominio pide "búscame", sin saber si responde Qdrant o Azure AI Search. Es la misma idea por la que `ChatService` no conoce Foundry (S2).

### 2.2 Nuevo puerto `QueryRewriter`

```python
class QueryRewriter(Protocol):
    def rewrite(self, messages: list[Message]) -> RewriteResult: ...
```

- **Por qué:** en S2 vimos que la memoria es historial. Si el cliente pregunta "¿y cuánto demora?", esa frase sola no sirve para buscar. El rewriter la convierte en "¿cuánto demora el reclamo por cargo no reconocido?".
- `SearchQuery` y `RewriteResult` (en [models.py](src/agent/domain/models.py)) siguen la misma idea de `AgentReply` en S2: **salida estructurada y validada** (`_not_blank`). El rewrite también devuelve `Usage`, y por eso `Usage` es sumable con `+`: en S4 un turno puede tener varias llamadas al modelo (rewrite y respuesta).

### 2.3 `ChatModel.stream` y eventos

`ChatModel` ganó el método `stream`, que entrega `IntentDetected` → `AnswerDelta`… → `ModelResult`. El cliente ve la respuesta mientras se escribe. El orden de los campos de `AgentReply` (`intent`, `answer`, `sources`) existe justo para eso: la intención llega primero.

### 2.4 `AgentReply.sources` y `Citation`

`AgentReply` ahora exige `sources: list[int]`, que son los números de los fragmentos que el modelo usó. Con ellos se arma `Citation` (`source`, `section`, `chunk_id`) para responder "según la sección X del documento Y".

> Lección de los tests: al volver `sources` obligatorio, los fakes que creaban `AgentReply` sin `sources` fallaron con `Field required` (11 fallos). En Pydantic, un campo sin valor por defecto es obligatorio, y cambiar el contrato obliga a actualizar los fakes.

### 2.5 [qdrant_knowledge_base.py](src/agent/infrastructure/search/qdrant_knowledge_base.py): búsqueda híbrida local

| Cambio | Por qué |
|---|---|
| `search` hace dos búsquedas y las fusiona | Ver secciones 3 y 5. |
| Filtro `still_valid` (`valid_until < hoy` queda fuera) | Un documento vencido no debe responder. Se filtra **antes** de buscar, no después. |
| `_client()` como `contextmanager` + `threading.Lock` | El modo local de Qdrant bloquea la carpeta: solo admite un cliente abierto a la vez. Se abre y se cierra en cada operación para que `ingest publish` no choque con el chat. |
| `CANDIDATES_PER_SEARCH = 20` | Cada búsqueda trae 20 candidatos antes de fusionar. Luego se recorta a `top_k`. |
| `MAX_CHUNKS_READ = 10_000` | Techo de chunks que se leen para la búsqueda por palabras. |

### 2.6 [hybrid.py](src/agent/infrastructure/search/hybrid.py): BM25 y RRF hechos en Python

- `split_into_words`: quita tildes y mayúsculas, así "Débito" y "debito" cuentan como la misma palabra.
- `keyword_scores`: implementa **BM25** (sección 3.2).
- `fuse_rankings`: implementa **Reciprocal Rank Fusion** (sección 3.3).

### 2.7 [azure_search_knowledge_base.py](src/agent/infrastructure/search/azure_search_knowledge_base.py): el mismo puerto sobre Azure AI Search

Implementa `publish`, `count` y `search`, pero el trabajo pesado lo hace el servicio: búsqueda híbrida, fusión y **reranking semántico**. Ver la sección 6.

### 2.8 Fakes de prueba ([fakes.py](tests/fakes.py))

- `FakeKnowledgeBase`: devuelve chunks fijos y anota qué se buscó, sin Qdrant ni red.
- `FakeEmbedder`: vectores falsos de 8 dimensiones.
- `FakeChatModel` ahora tiene `stream`, `rewrite` y `sources`.
- `InterruptedChatModel` simula una conexión que se corta a mitad de respuesta.

Es el mismo principio de S2: probar el caso de uso **sin Foundry**.

### 2.9 Pendiente en el código (estado actual)

- [chat_service.py](src/agent/application/chat_service.py) todavía no llama a `rewrite` ni a `search`. El flujo RAG completo en `/chat` aún no está conectado.
- [settings.py](src/agent/infrastructure/config/settings.py) todavía no tiene la variable `KNOWLEDGE_BASE`, aunque los comentarios del código la mencionan.
- [cli.py](src/agent/infrastructure/ingestion/cli.py) solo publica en `local` (Qdrant). `azure_search` llega en S5.

## 3. Conceptos

### 3.1 Búsqueda vectorial (por significado), lo que ya teníamos en S3

La pregunta se convierte en vector con el **mismo** modelo de embeddings que usó la ingesta (S3). Luego se buscan los chunks cuyo vector apunta en la dirección más parecida (`COSINE`).

- **Fuerte en:** sinónimos y paráfrasis. "Me clonaron la tarjeta" encuentra "uso no autorizado".
- **Débil en:** palabras exactas, códigos y términos raros como "contracargo", "SBS" o un número de artículo.

### 3.2 Búsqueda por palabras clave (BM25)

BM25 da puntos a un chunk por cada palabra de la pregunta que contiene:

- **Más puntos si la palabra es rara** en el corpus (`rarity`). "contracargo" vale más que "el".
- **Repetir la palabra suma cada vez menos** (`REPETITION_LIMIT = 1.5`).
- **Los chunks largos se penalizan** (`LENGTH_PENALTY = 0.75`), porque tienen más palabras por azar.

- **Fuerte en:** términos exactos.
- **Débil en:** sinónimos. "Bloqueo" no encuentra "suspensión".

### 3.3 ¿Qué es la búsqueda híbrida?

Es **ejecutar las dos búsquedas y combinar sus rankings**. Cada una tapa el punto débil de la otra.

Para combinar se usa **RRF (Reciprocal Rank Fusion)**: cada lista le da `1 / (60 + puesto)` a cada chunk, y se suman los puntos. No se comparan los scores (coseno y BM25 están en escalas distintas). Se compara **en qué puesto quedó** cada chunk en cada lista.

Ejemplo del test [test_qdrant_knowledge_base.py](tests/infrastructure/test_qdrant_knowledge_base.py):

| Chunk | Ranking por significado | Ranking por palabras ("contracargo") | RRF |
|---|---|---|---|
| A1 "plazo para reclamos" | 1.º → 1/61 | no aparece | 0.0164 |
| A2 "contracargo de compras" | 2.º → 1/62 | 1.º → 1/61 | **0.0325** |

A2 gana porque aparece en las dos listas. Es la regla de RRF: **gana lo que sale arriba en varios rankings.**

### 3.4 ¿Qué es top-k?

`top_k` es **cuántos chunks se devuelven como máximo**, ordenados del más al menos relevante. `top_k=5` significa "tráeme los 5 mejores".

- **Muy bajo:** se puede perder el chunk con la excepción de la regla (el riesgo que vimos en S3 con chunks de 250 caracteres).
- **Muy alto:** el prompt crece, sube el costo en `prompt_tokens` (visible en `Usage`, S2) y el modelo recibe ruido.

No hay que confundirlo con `CANDIDATES_PER_SEARCH` / `VECTOR_NEIGHBORS = 20`: esos son los **candidatos** que trae cada búsqueda antes de fusionar. `top_k` es el corte **final**.

```
20 por significado ─┐
                    ├─► fusión RRF ─► recorte a top_k ─► modelo
20 por palabras ────┘
```

### 3.5 ¿Qué es reranking?

El **reranking** es una segunda pasada que **reordena** los candidatos ya encontrados con un modelo más inteligente y más caro. Ese modelo lee la pregunta y el chunk **juntos** y juzga si el chunk realmente responde.

- La búsqueda (vector + BM25) es rápida y encuentra candidatos.
- El reranker es lento y preciso, y por eso solo se aplica a esos pocos candidatos.

**Importante:** RRF **no** es reranking. RRF solo mezcla posiciones y no entiende el texto. En nuestro código:

- **Qdrant local:** hay fusión (RRF), pero **no hay reranker**.
- **Azure AI Search:** `query_type="semantic"` activa el **semantic ranker** de Microsoft. Por eso el adaptador usa `@search.reranker_score` cuando existe.

### 3.6 Reescritura de la pregunta (query rewrite)

Antes de buscar, el modelo reescribe la última pregunta para que se entienda **sin el historial**. Une la memoria de S2 con la búsqueda de S4: el historial no se manda al buscador, se manda una pregunta autocontenida.

| Historial | Pregunta del cliente | Pregunta reescrita para buscar |
|---|---|---|
| "No reconozco un cargo de mi tarjeta" | "¿y cuánto demora?" | "¿Cuánto demora el reclamo por un cargo no reconocido en tarjeta?" |

## 4. Cómo se manejan ahora los chunks (S3 vs. S4)

| Aspecto | S3 | S4 |
|---|---|---|
| Para qué se usa el chunk | Se guarda con su vector | Se **busca** por vector **y** por palabras |
| `content` con ruta de títulos (`Reglamento > 4. Plazos`) | Daba contexto al embedding | Además suma palabras a BM25. Buscar "plazos" también encuentra la sección por su título |
| `valid_from` / `valid_until` | Metadata copiada del manifest | Se **usa**: los chunks vencidos se excluyen antes de buscar. Por ejemplo, `card-blocking-policy-2022.md` vence el `2024-12-31` y ya no responde |
| `id` UUID5 estable | Para que Qdrant lo acepte | Además permite republicar sin duplicar, en Qdrant y en AI Search |
| Publicar | Qdrant borra los chunks de esas fuentes y vuelve a insertar | Igual en Qdrant. **AI Search sube primero y luego borra** los chunks viejos (`search.in(source, ...)`), así el índice nunca queda vacío mientras el agente busca |
| Resultado de búsqueda | No existía | `SearchHit` (chunk + score). El modelo cita sus números en `sources` y se arma `Citation` |
| Tamaño (`INGEST_CHUNK_MAX_CHARS`) | Precisión vs. contexto ([RESULTS.md](RESULTS.md)) | Ahora pesa más. Con `top_k` fijo, chunks chicos dan más precisión, pero la regla y su excepción pueden quedar separadas y una puede quedar fuera del top-k |

## 5. Flujo de una pregunta con RAG (cuando se conecte en `ChatService`)

```
Cliente → /chat
  1. historial (S2)
  2. rewrite(historial + pregunta)  → pregunta autocontenida      [QueryRewriter]
  3. embed(pregunta)                → vector                      [Embedder, S3]
  4. search(texto, vector, top_k)   → SearchHit[]                 [KnowledgeBase, S4]
       ├─ filtro de vigencia
       ├─ vector (20) + BM25 (20) → RRF
       └─ (AI Search) reranking semántico
  5. complete(system + fragmentos numerados + historial + pregunta) → AgentReply(intent, answer, sources)
  6. sources → Citation(source, section, chunk_id)
  7. guardar en memoria (S2) y devolver respuesta con citas y Usage sumado (rewrite + respuesta)
```

## 6. ¿Cómo nos facilita Azure AI Search lo que hacemos por código?

Hoy, con Qdrant local, **nosotros** programamos BM25, RRF, el filtro de vigencia y el control de bloqueo. En Azure AI Search, todo eso es **configuración del índice y parámetros de la consulta**.

| Tema | Qdrant local + código propio | Azure AI Search |
|---|---|---|
| Dónde vive | Carpeta `data/index/<dominio>/`, embebido en el proceso | Servicio administrado en Azure |
| Búsqueda vectorial | `query_points` (compara contra **todos** los vectores) | `VectorizedQuery` con índice **HNSW** (aproximado, escala a millones) |
| Búsqueda por palabras | BM25 escrito a mano en `hybrid.py`; lee hasta 10 000 chunks en **cada** búsqueda | Índice invertido nativo, con analizador `es.microsoft` (raíces, plurales y acentos en español) |
| Tildes y mayúsculas | `split_into_words` hecho por nosotros | Lo hace el analizador del idioma |
| Fusión híbrida | `fuse_rankings` (RRF) escrito a mano | RRF automático al enviar `search_text` + `vector_queries` |
| Reranking | **No hay** | Semantic ranker con `query_type="semantic"` y `@search.reranker_score` |
| Campo título / contenido | Todo va dentro de `content` | `SemanticConfiguration`: `section` como título y `content` como contenido |
| Filtro de vigencia | `models.Filter` + `DatetimeRange` | Filtro OData: `valid_until eq null or valid_until ge <hoy>` |
| Concurrencia | `threading.Lock`: un solo cliente por carpeta, un solo proceso | Muchas réplicas y procesos a la vez |
| Escala | Miles de chunks por dominio | Millones de documentos, con particiones y réplicas |
| Publicar sin cortar el servicio | Borra y luego inserta (hay un instante sin datos) | Sube y luego borra lo obsoleto |
| Costo | Gratis, local | Pago por servicio (tier) y por uso del semantic ranker |
| Ideal para | Desarrollo, laboratorio, pruebas sin red | Producción, varios equipos y dominios |

**Idea clave:** gracias al puerto `KnowledgeBase`, cambiar de Qdrant a AI Search **no toca** `ChatService` ni el dominio. Solo cambia el adaptador que elige `bootstrap.py`. Es la misma promesa de arquitectura que vimos en S2 (Foundry detrás de `ChatModel`) y en S3 (Foundry detrás de `Embedder`).

## 7. Resumen para explicar en una frase

- **Búsqueda híbrida:** buscar por significado y por palabras exactas a la vez, y combinar los resultados.
- **RRF:** mezcla rankings por posición; gana lo que sale arriba en varias listas.
- **top-k:** cuántos fragmentos finales se le dan al modelo.
- **Reranking:** una segunda pasada inteligente que reordena los candidatos leyendo pregunta y fragmento juntos.
- **Rewrite:** convertir "¿y cuánto demora?" en una pregunta que se entiende sola, para poder buscarla.
- **AI Search:** lo que hoy escribimos a mano (BM25, RRF, filtros, concurrencia) pasa a ser configuración, y además agrega reranking.
