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



## Conclusión

La línea base de Foundry muestra resultados sólidos en recuperación, intención, apoyo y relevancia. A diferencia de las corridas locales con mock, esta evaluación permite medir respuestas generadas por un modelo real. Para la siguiente iteración, conviene revisar las discrepancias en la verificación de hechos y evitar que el agente responda con información de fuentes prohibidas ante consultas fuera del dominio.

Detalle de la evaluación: `data/eval/fraud-20261119-134644.json`