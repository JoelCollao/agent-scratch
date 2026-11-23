# RESULTS: libreta del equipo

Mediciones y decisiones del equipo sobre la ingesta. El `README.md` del proyecto no se toca.

## Tamaño de chunk: `INGEST_CHUNK_MAX_CHARS`

Corpus de dominio `fraud`: 13 documentos.

| `INGEST_CHUNK_MAX_CHARS` | Chunks | Promedio (caracteres) | Máximo | Mínimo |
|---|---|---|---|---|
| 250 | 66 | 230 | 347 | 126 |
| 1500 | 51 | 272 | 644 | 126 |

Medido con el chunker sobre el corpus, sin embeddings.

### Por qué cambia el número

- El chunker corta primero por sección. Cada sección es como mínimo un chunk, y las secciones cortas no se unen con sus vecinas.
- `max_chars` solo parte una sección que supera el límite. Con 250, muchas secciones se parten en varios chunks; con 1500, casi todas caben enteras.
- Por eso el mínimo (126) es igual en ambos casos, y el máximo de 1500 nunca se alcanza: el corpus tiene pocas secciones largas.
- Un párrafo o una oración más larga que el límite no se corta. Por eso con 250 el máximo es 347.

Diferencias más visibles por documento:

| Documento | 250 | 1500 |
|---|---|---|
| `claims-regulation.pdf` | 16 | 10 |
| `card-blocking-policy.docx` | 7 | 5 |
| `response-times.csv` | 5 | 1 |
| `credit-card-chargebacks.html` | 5 | 4 |
| `sample-cases.pdf` | 4 | 3 |
| `unrecognized-charges-procedure.md` | 5 | 4 |

### Qué se gana con 250

- **Precisión:** cada chunk habla de una sola cosa. Una búsqueda sobre "plazo de respuesta" devuelve el párrafo del plazo, no toda la sección.
- **Tablas:** `response-times.csv` pasa de 1 a 5 chunks, uno por tramo de filas, cada uno con su encabezado.

### Qué se pierde con 250

- **Contexto:** una regla y su excepción pueden quedar en chunks distintos. Ejemplo: "15 días hábiles" en un chunk y "salvo fraude con tarjeta, 30 días" en otro. El modelo podría recuperar solo uno de los dos.
- **Más chunks:** más vectores que guardar y más llamadas al embedder en `build`.

### Pendiente

- Revisar con `uv run python dev/show_chunks.py <fuente>` si las excepciones quedaron junto a su regla en `claims-regulation.pdf` con 250.
- Decidir el valor final. Hasta entonces, el `.env` tiene `INGEST_CHUNK_MAX_CHARS=250`.
