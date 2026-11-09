## Qué significan las métricas

- **Latencia:** tiempo medido por el adaptador para la llamada al modelo.
- **Tokens de entrada:** consumo reportado para el contexto enviado; no solo la última pregunta.
- **Tokens de salida:** consumo de salida reportado por el proveedor.

El cliente muestra los valores de `usage` recibidos desde la API; no los calcula.

## Cuadro de resultados - Modelo: gpt-5-mini

Resultados reportados desde la consola durante las pruebas del lab. Los mensajes se conservan tal como fueron enviados.


| Mensaje | Intención | latency_ms | prompt_tokens | completion_tokens |
|---|---|---|---|---|
| HOLA | greeting | 3257 | 379 | 199 |
| cuales son los procedmiento para bloquear mi tarjeta | product_question | 6375 | 453 | 838 |
| quiero ver mi fondos que me robaron debido al fraude | data_query | 6268 | 651 | 784 |
| boquea mis tarjetas por el fraude | sensitive_action | 7063 | 857 | 876 |
| que es un gis? | out_of_scope | 6636 | 1026 | 613 |

## Cuadro de resultados - Modelo: gpt-5-nano

Resultados reportados desde la consola al probar `gpt-5-nano`. Los mensajes se conservan tal como fueron enviados; algunos difieren de los usados con `gpt-5-mini`.

| Mensaje | Intención | latency_ms | prompt_tokens | completion_tokens |
|---|---|---|---|---|
| Hola | greeting | 6305 | 378 | 307 |
| Cuales son los procedmiento para bloquear mi tarjeta | product_question | 8490 | 432 | 1751 |
| quiero ver mi fondos que me robaron debido al fraude | data_query | 6782 | 588 | 1437 |
| bloquea mis tarjetas por el frauden de | sensitive_action | 6542 | 683 | 1131 |
| quiero ceviche | out_of_scope | 2698 | 785 | 307 |

## COSTO-MES

### Escenario medido

- Modelo reportado para la prueba: **gpt-5-nano**.
- Configuración: **`MAX_TURNS=10`** (el nombre de la variable es plural).
- Una conversación de **20 preguntas consecutivas**, conservando el mismo `session_id`.
- Proyección: repetir una conversación de consumo equivalente cada día durante **30 días**, es decir, **600 preguntas al mes**.
- Se supone una sesión nueva cada día. No es una medición de 600 preguntas en una única sesión ni de 20 sesiones independientes por día.
- Las cifras siguientes provienen del historial de consola proporcionado, no de una factura de Azure.

### Consumo por pregunta

| Turno | Mensaje | latency_ms | prompt_tokens | completion_tokens |
|---|---|---|---|---|
| 1 | Hola, necesito ayuda con un posible fraude. | 8579 | 386 | 1377 |
| 2 | Detecté un cargo que no reconozco de S/ 180 en el comercio ficticio Tienda Sol. | 9288 | 497 | 1524 |
| 3 | El cargo fue ayer y corresponde a mi tarjeta de débito. ¿Qué debo hacer primero? | 8768 | 623 | 1544 |
| 4 | Todavía tengo la tarjeta conmigo. ¿Puede existir fraude aunque no la haya perdido? | 6299 | 768 | 1031 |
| 5 | ¿Cuál es el procedimiento para bloquearla? | 7723 | 898 | 1360 |
| 6 | Antes de continuar, ¿qué monto y comercio te indiqué? | 5148 | 1045 | 965 |
| 7 | ¿Qué diferencia hay entre un bloqueo temporal y uno definitivo? | 7227 | 1117 | 1045 |
| 8 | Quiero solicitar el bloqueo temporal de mi tarjeta de débito. ¿Qué confirmación necesitas? | 8334 | 1273 | 1478 |
| 9 | No ejecutes ninguna acción todavía. ¿Qué datos puedo proporcionar sin compartir información sensible? | 6628 | 1415 | 1220 |
| 10 | ¿Qué documentos o evidencias debería reunir para reclamar? | 12173 | 1550 | 1923 |
| 11 | ¿Cuánto tiempo tengo para presentar el reclamo? Si no conoces el plazo del banco, indícalo | 5362 | 1812 | 814 |
| 12 | ¿Qué monto y comercio mencioné al comienzo de esta conversación? | 4369 | 1829 | 638 |
| 13 | ¿Cómo puedo revisar si existen otros movimientos no reconocidos? | 5261 | 1764 | 770 |
| 14 | Encontré otro cargo ficticio de S/ 75 en Tienda Luna. ¿Debo incluirlo en el mismo reclamo? | 6689 | 1823 | 1089 |
| 15 | ¿Cuál es el monto total de los dos cargos que te mencioné? | 3702 | 1821 | 438 |
| 16 | ¿Qué diferencia existe entre un reclamo por movimiento no reconocido y un contracargo? | 9186 | 1740 | 1511 |
| 17 | ¿Puedes consultar el estado de mi reclamo o necesitas acceso a una herramienta del banco? | 6755 | 1841 | 1239 |
| 18 | ¿Qué tipo de tarjeta indiqué y qué bloqueo solicité? | 8476 | 1842 | 1285 |
| 19 | Si alguien me llama pidiendo mi clave para devolverme el dinero, ¿qué debo hacer? | 11004 | 1841 | 1281 |
| 20 | Resume mi caso: comercios, montos, tipo de tarjeta y bloqueo solicitado. Señala cualquier dato que ya no tengas en el contexto. | 15365 | 1908 | 2147 |
| **Total de tokens** | **20 preguntas** | — | **27793** | **24679** |

El total diario es **52472 tokens** entre entrada y salida. No hay que sumar otra vez el historial: ya forma parte de `prompt_tokens` en cada llamada. La latencia no interviene en el precio por tokens. Los tokens de salida reportados pueden incluir razonamiento del modelo, no solo el texto visible.

### Tarifas y alcance de la estimación

Para dar una cifra reproducible, se usan estas **tarifas públicas de referencia de la API de OpenAI**, consultadas el 8 de noviembre de 2026:

| Concepto | USD por 1000000 tokens |
|---|---|
| Entrada sin caché | 0.05 |
| Entrada en caché | 0.005 |
| Salida | 0.40 |

Fuente: [precios publicados de GPT-5 nano](https://developers.openai.com/api/docs/models/gpt-5-nano).

**Tu aplicación usa Azure: estas tarifas de referencia no son una cotización confirmada de tu deployment de Azure.** La consulta al catálogo público de precios de Azure para `gpt-5-nano` no devolvió tarifas y la página de precios mostró valores sin importe. Confirma región, modalidad de deployment y tarifas de tu oferta en [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/azure-openai/) o en la calculadora de Azure. Si son distintas, sustituye los precios en la fórmula.

El cálculo trata **toda la entrada como no cacheada**, porque la consola no separa `cached_tokens`. No aplica Batch, descuentos, impuestos, conversión a soles, infraestructura ni otros servicios. Es una estimación del consumo del modelo, no del costo completo de operar el agente.

### Cálculo diario y mensual

```text
Costo diario de entrada = 27793 / 1000000 × USD 0.05
                        = USD 0.00138965

Costo diario de salida  = 24679 / 1000000 × USD 0.40
                        = USD 0.00987160

Costo diario total      = USD 0.01126125

Costo mensual (30 días) = USD 0.01126125 × 30
                        = USD 0.33783750 ≈ USD 0.34
```

| Periodo | Preguntas | Tokens de entrada | Tokens de salida | Costo de entrada (USD) | Costo de salida (USD) | Total estimado (USD) |
|---|---|---|---|---|---|---|
| Un día | 20 | 27793 | 24679 | 0.00138965 | 0.00987160 | 0.01126125 |
| Mes de 30 días | 600 | 833790 | 740370 | 0.04168950 | 0.29614800 | **0.33783750** |

**Respuesta:** con este consumo y las tarifas de referencia indicadas, preguntar 20 veces al día costaría aproximadamente **USD 0.34 por mes de 30 días**, solo por tokens del modelo. Para 31 días, sería aproximadamente **USD 0.35**. No se garantiza ese importe en tu factura de Azure.

Para usar las tarifas reales de tu deployment, con precios por millón:

```text
Costo mensual = 0.833790 × precio de entrada
              + 0.740370 × precio de salida
```

Si existe caché, separa la entrada cacheada de la no cacheada antes de aplicar cada precio.

### ¿Qué cambiaría con `MAX_TURNS=4`?

En [chat_service.py](src/agent/application/chat_service.py), el historial enviado se selecciona así:

```python
recent = self.store.get(session_id)[-self.max_turns * 2 :]
```

- **Con 10:** envía hasta 20 mensajes previos (10 pares usuario/asistente).
- **Con 4:** envía hasta 8 mensajes previos (4 pares).
- En ambos casos se agregan el prompt del sistema y la pregunta actual.
- La diferencia de ventana aparece en la **pregunta 6**: ya hay cinco turnos anteriores y la configuración 4 descarta el más antiguo.
- El historial almacenado en RAM no se borra con este recorte; cambia lo enviado al modelo.

**Normalmente disminuirá el consumo de entrada**, porque se reenvían menos preguntas y respuestas antiguas. Pero **no significa que el costo total baje un 60 %**: el prompt fijo y la pregunta actual siguen presentes; las respuestas y su razonamiento pueden cambiar, y el uso de caché también puede variar.

En esta estimación, la salida cuesta USD 0.296148 al mes y la entrada USD 0.04168950. Por eso, reducir solo el historial tiene un impacto limitado si la salida se mantiene igual. No podemos calcular el ahorro real con 4 a partir de esta única prueba con 10.

También puede empeorar la memoria: el modelo puede olvidar comercios, montos o preferencias anteriores. Si una respuesta reciente repite esos datos, podrían seguir disponibles aunque el mensaje original ya no esté en la ventana.

### Prueba pendiente para comparar costos

Reinicia el servidor con `MAX_TURNS=4`, inicia una sesión nueva y repite las mismas 20 preguntas en el mismo orden, sin escribir `nueva` entre ellas. Mantén modelo, prompt y condiciones de generación; no recuerdes al agente los datos que olvide.

| Configuración | Preguntas por día | Total diario prompt_tokens | Total diario completion_tokens | Costo mensual referencial (USD, 30 días) |
|---|---|---|---|---|
| MAX_TURNS=10 | 20 | 27793 | 24679 | 0.33783750 |
| MAX_TURNS=4 | 20 | Pendiente de medir | Pendiente de medir | Pendiente de calcular |

```text
Costo mensual con 4 = 30 × (
    total diario de entrada con 4 × precio de entrada / 1000000
  + total diario de salida con 4 × precio de salida / 1000000
)

Ahorro mensual = costo mensual con 10 − costo mensual con 4
```

Repite ambas pruebas varias veces y promedia para una estimación más fiable. Compara también si conserva el contexto: menor costo no basta si se pierde información necesaria para atender el caso.

### Proyección para miles de clientes del banco

Para dimensionar el dominio de fraude, se debe proyectar por **conversaciones mensuales y preguntas por conversación**, no solo por personas. Un cliente puede iniciar varias conversaciones y cada una puede tener una longitud diferente.

Como escenario de referencia, se supone:

- Modelo `gpt-5-nano` y `MAX_TURNS=10`.
- Cada cliente atendido inicia **una conversación de 20 preguntas**.
- Cada conversación consume lo mismo que la prueba: **27793 tokens de entrada y 24679 de salida**.
- Mes de **30 días** y costo referencial de **USD 0.01126125 por conversación**.
- Se mantienen las tarifas de referencia y exclusiones de la sección COSTO-MES; **no son precios confirmados de tu deployment Azure**.

| Clientes atendidos al día | Conversaciones al mes | Preguntas al mes | Tokens de entrada al mes | Tokens de salida al mes | Costo mensual referencial (USD) |
|---|---|---|---|---|---|
| 1000 | 30000 | 600000 | 833790000 | 740370000 | **337.84** |
| 5000 | 150000 | 3000000 | 4168950000 | 3701850000 | **1689.19** |
| 10000 | 300000 | 6000000 | 8337900000 | 7403700000 | **3378.38** |
| 50000 | 1500000 | 30000000 | 41689500000 | 37018500000 | **16891.88** |

Los costos se calculan con el valor por conversación sin redondear y se redondean al final. Los clientes atendidos por día no equivalen necesariamente a clientes únicos en el mes.

```text
Conversaciones mensuales =
    clientes atendidos al día × conversaciones por cliente × 30

Costo mensual =
    conversaciones mensuales × costo promedio por conversación
```

#### Cómo obtener una proyección más realista

La prueba de 20 preguntas no representa todas las consultas bancarias. Mide varias conversaciones cortas, medianas y largas —por ejemplo, de **3, 8 y 20 preguntas**— y calcula por separado su consumo promedio. Usa datos de tráfico o un piloto para estimar qué proporción corresponde a cada grupo.

```text
Costo mensual =
    conversaciones cortas × costo promedio corto
  + conversaciones medianas × costo promedio mediano
  + conversaciones largas × costo promedio largo
```

No supongas que una conversación de 3 preguntas cuesta exactamente 3/20 de una de 20: el contexto crece y luego se recorta según `MAX_TURNS`. También cambian la longitud de las respuestas y el razonamiento generado.

Registra volumen, longitud de conversación, tokens de entrada/salida y caché durante un piloto. Sustituye las tarifas de referencia por las de Azure que apliquen a tu región, modalidad y contrato.

#### Consumo del modelo no es el costo completo del servicio

Presupuesta por separado infraestructura de la API, almacenamiento de historial, búsqueda/RAG, herramientas, monitoreo y llamadas adicionales al modelo. El promedio diario tampoco determina la capacidad necesaria: hay que medir horas pico y concurrencia para validar las cuotas de solicitudes y tokens por minuto.

En un banco, compara costo con calidad: respuestas que inventan procedimientos, pierden datos del caso o prometen acciones que no pueden ejecutar no son aceptables aunque consuman menos tokens. Las acciones sensibles requieren controles y confirmación; una intención detectada no prueba que se haya realizado un bloqueo o reclamo.

## Selección de modelo según la intención

### ¿Conviene un modelo chico para `greeting` y `out_of_scope`, y uno grande solo para el resto?

**Sí, conviene evaluar un modelo pequeño para `greeting` y `out_of_scope`**, porque suelen requerir respuestas simples. Reservaría un modelo más capaz para consultas complejas de fraude, siempre que las pruebas demuestren una mejora de calidad que justifique su costo.

Para hacerlo, necesitamos un clasificador o enrutador que determine la intención **antes de elegir el modelo que responderá**. El ahorro debe considerar el costo de esa clasificación y evitar que mensajes importantes, como “Hola, me robaron la tarjeta”, se traten como un simple saludo.

### Precisiones importantes

- **`out_of_scope` significa “fuera del ámbito del agente”**, no “no tengo conocimiento”. El modelo puede saber qué es un GIS, pero debe aplicar la política del banco sobre temas ajenos a fraude, bloqueo y reclamos.
- **No todo el resto necesita un modelo grande:** consultas frecuentes pueden resolverse con uno pequeño y fuentes verificadas.
- Consultar datos o bloquear tarjetas requiere herramientas, permisos y confirmación. Un modelo más potente no reemplaza esos controles.
- La clasificación puede cometer errores y, si utiliza un modelo, agrega consumo y latencia. Debe incluirse en el costo total, no contabilizar únicamente la respuesta final.

### Conclusión

**Sí al enrutamiento, pero decidirlo con pruebas de costo total, latencia y precisión**, especialmente para no descartar casos de fraude. Esta es una propuesta de diseño; no significa que el enrutamiento entre modelos ya esté implementado en el agente.
