# Sesion 04 - Pruebas

## Paso 12 — Medir con `SEARCH_TOP_K`

**Entorno:** Qdrant local (`data/index/fraud`) y `dev/mock_foundry.py`; no se llamó a Foundry en la nube. Para cada valor se reinició el agente y se hicieron estos dos turnos en una misma conversación.

### Pregunta 1

> ¿Cuál es el plazo para presentar un reclamo?

**Respuesta observada:** Sí. El agente indicó que el plazo general es de 60 días calendario y citó `claims-regulation.pdf`, sección **3.1 Plazo para presentar**.

| `SEARCH_TOP_K` | Tokens de entrada | Tokens de salida | Observación |
|---:|---:|---:|---|
| 2 | 290 | 46 | Recuperó la sección del plazo. |
| 5 | 473 | 46 | Misma respuesta y fuente que con 2. |
| 10 | 733 | 46 | Misma respuesta y fuente; agregó fragmentos laterales al contexto. |

### Pregunta 2

> ¿y si es por fraude?

**Respuesta observada:** No respondió el plazo para presentar un reclamo por fraude. Devolvió un fragmento de `fraud-and-claims-faq.md` sobre el tiempo de respuesta (15 días hábiles), que es una pregunta distinta.

| `SEARCH_TOP_K` | Tokens de entrada | Tokens de salida | Fuente citada |
|---:|---:|---:|---|
| 2 | 407 | 53 | FAQ sobre «¿En cuánto tiempo me responden?» |
| 5 | 578 | 53 | La misma FAQ. |
| 10 | 858 | 53 | La misma FAQ. |

**Por qué no respondió:** el mock de reescritura usa solamente el último mensaje. Por eso `¿y si es por fraude?` llega al buscador sin la pregunta anterior y no expresa que el cliente pregunta por el plazo para presentar un reclamo. Subir `SEARCH_TOP_K` no corrigió ese problema; con 10 también entraron fragmentos laterales, como canales de atención, abono provisional, resultado del reclamo y costo de reposición de tarjeta.

**Qué habría que hacer para que responda:**

1. Reescribir la pregunta de seguimiento como una consulta independiente que conserve el contexto: **«¿Cuál es el plazo para presentar un reclamo por una operación fraudulenta o no reconocida?»**
2. Comprobar que esa consulta recupera entre sus primeros resultados el fragmento del reglamento o procedimiento que indique el plazo específico para fraude.
3. Si no aparece, revisar los términos de búsqueda y la sección/chunk del corpus; no asumir que aumentar `top_k` resolverá por sí solo la falta de contexto.
4. Volver a probar la respuesta y comprobar que la cita apunta a esa sección. El mock actual solo repite el primer fragmento, así que para evaluar la calidad de la respuesta generada se necesita una reescritura y un modelo que reflejen ese comportamiento.

## Comparación y decisión

| `SEARCH_TOP_K` | Entrada turno 1 | Entrada turno 2 |
|---:|---:|---:|
| 2 | 290 | 407 |
| 5 | 473 | 578 |
| 10 | 733 | 858 |

Con 5, la entrada aumentó **183** y **171** unidades respecto a 2. Con 10, aumentó **443** y **451**. Las respuestas y fuentes citadas no mejoraron al subir `top_k`.

**Elección provisional del equipo: `SEARCH_TOP_K=2`.** Para la pregunta directa recuperó la sección correcta; 5 y 10 no mejoraron las respuestas de estas pruebas y agregaron más contexto y consumo. Antes de considerarlo definitivo, hay que resolver y volver a medir la pregunta de seguimiento.

**Limitación de la medición:** el mock cuenta palabras separadas por espacios en lugar de usar un tokenizador real. Las cifras sirven para comparar estas corridas, pero no equivalen a tokens reales de Foundry. Además, el mock de respuesta solo usa y cita el fragmento número 1, por lo que la prueba no mide cómo un modelo real aprovecharía los fragmentos adicionales.
