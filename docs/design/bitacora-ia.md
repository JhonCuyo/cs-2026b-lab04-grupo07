# Bitácora de Uso de Inteligencia Artificial - San Camilo en Línea - Laboratorio 04

| # | Fecha | Herramienta | Prompt (Resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|---|---|---|---|---|---|
| 1 | 2026-09-29 | Claude | Generación de alternativas de arquitectura según RCRTF | Arquitectura de Microservicios con Kubernetes y RabbitMQ | Excede las restricciones R-01 (plazo de 1 mes), R-02 (equipo de 3) y R-03 (presupuesto bajo) | Rechazada |
| 2 | 2026-09-29 | ChatGPT | Crítica adversarial a Monolito Modular ("Abogado del diablo") | Señaló riesgos de acoplamiento de base de datos y caída total si falla un módulo | Se validó que aislando los esquemas en PostgreSQL y usando tareas asíncronas con Celery/Redis se mitigan los riesgos | Aceptada |
| 3 | 2026-09-30 | Gemini | Estrategia para PWA en celulares de gama baja | PWA con Service Workers y caché local para catálogos | Se verificó la compatibilidad con dispositivos Android de gama baja y señal 3G (QA-01) | Aceptada |
| 4 | 2026-09-30 | Copilot | Generación del código Mermaid para el flujo del sistema | Sintaxis Mermaid con subgraph y dependencias | Se corrigieron nombres de componentes y la dirección de las flechas hacia las APIs externas | Corregida |
| 5 | 2026-10-01 | Claude | Borrador de ADR-001 sobre el estilo arquitectónico | Estructura base del registro de decisión | Se ajustaron las consecuencias citando explícitamente los IDs de restricciones de drivers.md | Corregida |

---

## Anexo: Prompts Completos

### Prompt 1: Generación de alternativas (Rechazada / Evaluada)
> **Rol:** Arquitecto de Software Senior experto en soluciones para comercio local.  
> **Contexto:** Plataforma "San Camilo en Línea" para el Mercado San Camilo (Arequipa). Los comerciantes publican sus productos desde celulares de gama baja; los clientes realizan pedidos multi-puesto y pagan con Yape; las confirmaciones se envían por WhatsApp.  
> **Restricciones:** 3 desarrolladores, MVP funcional en 1 mes, único servidor VPS de bajo costo.  
> **Tarea:** Propón 3 alternativas de estilo arquitectónico indicando ventajas, desventajas y qué atributos de calidad favorece o penaliza.  
> **Formato:** Tabla comparativa en Markdown con recomendación final.

### Prompt 2: Crítica adversarial (Abogado del diablo)
> **Rol:** Arquitecto Evaluador Adversario.  
> **Contexto:** Hemos seleccionado una arquitectura de Monolito Modular para San Camilo en Línea.  
> **Tarea:** Critica esta decisión. Enumera los 5 riesgos más graves en producción dados nuestros límites de equipo y plazo, y sugiere tácticas de mitigación.

# Bitácora de Uso de IA - Laboratorio 05

## Interacción 1 - Generación inicial del Diagrama de Clases (E1)
* **Fecha:** 2026-10-07
* **Herramienta:** IA Generativa (ChatGPT / Claude / Gemini)
* **Prompt utilizado:**
  > "Actúa como diseñador software OO. Genera un diagrama de clases en PlantUML para el sistema San Camilo en Línea. Contexto: Pedido multipuesto a varios comerciantes con pago único con Yape/Plin (ADR-001 de puertos y adaptadores). Incluye atributos tipados, visibilidad, operaciones, multiplicidades y puertos/adaptadores."

* **Propuesta de la IA:**
  1. Propuso una clase `PagoIndividual` por cada puesto.
  2. Uso de herencia `Yape extends PasarelaPago`.
  3. Relación de agregación simple entre `PedidoMultipuesto` y `LineaPedido`.

* **Verificación y Decisión del Equipo:**
  1. **Rechazado:** La historia exige pago único, no pagos individuales por puesto. Se mantuvo un solo objeto `Pago` asociado a `PedidoMultipuesto`.
  2. **Corregido:** `PasarelaPago` debe ser una interfaz (puerto) implementada/realizada por `YapeAdapter` y `PlinAdapter`, según la regla de arquitectura limpia del ADR-001.
  3. **Corregido:** Se cambió la relación a Composición (`1 *-- 1..*`), ya que las líneas no tienen sentido sin el pedido (Regla C3).

## Interacción 2 - Generación del Diagrama de Secuencia (E2)
* **Fecha:** 2026-10-11
* **Herramienta:** IA Generativa (ChatGPT / Claude / Gemini)
* **Prompt utilizado:**
  > "Genera un diagrama de secuencia en PlantUML para el flujo 'confirmar y pagar pedido multipuesto con Yape' en San Camilo en Línea. Debe incluir: Comprador, UI, Controller, ServicioPedidos, RepositorioPedidos, PedidoMultipuesto, PasarelaPago y Notificador. Utiliza fragmentos 'alt' para éxito/error, 'loop' para reservar stock, y un mensaje asíncrono para notificar comerciantes por WhatsApp."

* **Propuesta de la IA:**
  1. Utilizó llamadas síncronas hacia el `Notificador` bloqueando la respuesta del servicio.
  2. Invocó un método `enviarSMS()` en la entidad `Comprador`.

* **Verificación y Decisión del Equipo:**
  1. **Corregido:** Se cambió la notificación a un mensaje asíncrono (`->>`) para que el envío de WhatsApp a múltiples puestos no demore la respuesta HTTP al usuario.
  2. **Corregido (Regla C1):** Se eliminó `enviarSMS()` ya que la notificación la gestiona el puerto `Notificador` y no la clase `Comprador`.

  ## Interacción 3 - Generación del Diagrama de Máquina de Estados (E3)
* **Fecha:** 2026-10-11
* **Herramienta:** IA Generativa (ChatGPT / Claude / Gemini)
* **Prompt utilizado:**
  > "Genera un diagrama de máquina de estados en Mermaid (stateDiagram-v2) para la entidad PedidoPuesto de 'San Camilo en Línea'. Incluye los estados: RECIBIDO, LISTO, RECOGIDO, ENTREGADO, RECHAZADO y CANCELADO. Agrega guardas entre corchetes y nombra las transiciones con operaciones de la clase."

* **Propuesta de la IA:**
  1. Utilizó el estado `EN_PREPARACION` sin asociarle una operación de transición clara.
  2. Omitió las guardas de validación de stock y llegada del repartidor.

* **Verificación y Decisión del Equipo:**
  1. **Corregido (Regla C2):** Se simplificó la transición a `marcarListo()` para coincidir exactamente con el método de la clase `PedidoPuesto`.
  2. **Corregido:** Se agregaron las guardas `[comerciante termina preparacion]` y `[repartidor llega al puesto]` para cumplir los criterios de aceptación y los estados sugeridos de la guía.

## Interacción 4 - Generación del Diagrama de Actividades (E4)
* **Fecha:** 2026-10-11
* **Herramienta:** IA Generativa (ChatGPT / Claude / Gemini)
* **Prompt utilizado:**
  > "Genera un diagrama de actividades en PlantUML para la 'preparación y consolidación de un pedido multipuesto' en San Camilo en Línea. Incluye 3 particiones (Comprador, Sistema/Repartidor, Comerciante), decisiones de stock y pago, bifurcación paralela (fork/join) y la entrega final."

* **Propuesta de la IA:**
  1. No incluyó la etapa de acopio/consolidación de los paquetes de los diferentes puestos antes del despacho.
  2. Colocó al comerciante entregando directamente al comprador de forma individual.

* **Verificación y Decisión del Equipo:**
  1. **Corregido (Feedback de usuario):** Se ajustó el diagrama agregando la partición de acopio y consolidación por parte del repartidor en el mercado San Camilo antes del envío, para cumplir con el concepto de entrega única de la historia de usuario HU-07.

## Interacción 5 - Generación del Diagrama de Paquetes (E5)
* **Fecha:** 2026-10-11
* **Herramienta:** IA Generativa (ChatGPT / Claude / Gemini)
* **Prompt utilizado:**
  > "Genera un diagrama de paquetes en PlantUML para el monolito modular de San Camilo en Línea con los paquetes: catalogo, pedidos, pagos, notificaciones, reportes y compartido. Etiqueta las dependencias con sus respectivos puertos/clases y agrega una nota que asegure el cumplimiento de la regla C4 sin ciclos."

* **Propuesta de la IA:**
  1. Dibujó una relación directa bidireccional entre `pagos` y `pedidos` (`PAG ..> PED` y `PED ..> PAG`).
  2. Involucró al paquete `reportes` como dependencia directa de `notificaciones`.

* **Verificación y Decisión del Equipo:**
  1. **Corregido (Regla C4):** Se eliminó la dependencia de `pagos` hacia `pedidos`. La comunicación es unidireccional utilizando el puerto `PasarelaPago`, evitando acoplamiento cíclico[cite: 4, 12].
  2. **Corregido:** Se mantuvieron las dependencias comunes hacia el paquete `compartido` para mantener el aislamiento entre módulos.

  ## Interacción 6 - Generación de Código e Ingeniería Inversa (E6)
* **Fecha:** 2026-10-11
* **Herramienta:** IA Generativa (ChatGPT / Claude / Gemini)
* **Prompt utilizado:**
  > "Genera el esqueleto en Python 3.10+ (utilizando dataclasses, Enum, Decimal, UUID y ABC) a partir del diagrama de clases PlantUML del modulo pedidos de San Camilo en Linea. Respeta exactamente los nombres en snake_case, tipos y metodos con NotImplementedError para adaptadores."

* **Propuesta de la IA:**
  1. Utilizó listas genéricas sin tipado de elementos (`lineas: list`).
  2. Implementó la interfaz `PasarelaPago` como una clase concreta sin heredar de `ABC`.

* **Verificación y Decisión del Equipo:**
  1. **Corregido:** Se especificaron colecciones fuertemente tipadas (`list[LineaPedido]`) para permitir que herramientas de análisis estático como `pyreverse` detecten los tipos de las clases asociadas.
  2. **Corregido:** Se heredó de `ABC` y se añadió el decorador `@abstractmethod` en `PasarelaPago` para representar adecuadamente la interfaz/puerto en Python.

  ## Interacción 7 - Auditoría de Consistencia C1-C5 (E7)
* **Fecha:** 2026-10-11
* **Herramienta:** IA Generativa (ChatGPT / Claude / Gemini)
* **Prompt utilizado (Prompt IA 3):**
  > "Actúa como auditor de diseño de software. Analiza los 5 diagramas PlantUML/Mermaid adjuntos (clases, secuencia, estados, actividades y paquetes) del sistema San Camilo en Línea. Verifica las reglas C1 (mensajes de secuencia = operaciones), C2 (transiciones de estado = operaciones), C3 (multiplicidades de negocio), C4 (paquetes sin ciclos) y C5 (consistencia de nombres del dominio). Responde en una tabla con: Regla, Elemento, Hallazgo y Corrección sugerida."

* **Propuesta de la IA:**
  1. Reportó un error C1 alegando que `Notificador` no tenía operaciones asignadas.
  2. Identificó la falta del método `recogerPedido()` en la clase `PedidoPuesto` para la regla C2.
  3. Aseguró que el paquete `pagos` dependía cíclicamente de `pedidos` (regla C4).

* **Verificación y Decisión del Equipo:**
  1. **Falso positivo C1 identificado:** Se constató que `Notificador` declara `notificarNuevoPedido()`.
  2. **Hallazgo aceptado C2:** Se incluyó `recogerPedido()` en `clases.puml`.
  3. **Falso positivo C4 identificado:** Se verificó el diagrama `paquetes.puml`, confirmando que la flecha es unidireccional `PED ..> PAG` a través del puerto `PasarelaPago`.

# Bitácora de Uso de IA — Laboratorio 06 (Modelo C4)

Registro de interacciones con IA generativa siguiendo la regla de oro: *"La IA propone, el equipo decide y verifica"*.

---

### Interacción 1: Generación del borrador inicial de `workspace.dsl` (Nivel 1 y Nivel 2)
* **Fecha:** 2026-10-13
* **Herramienta:** Gemini / Asistente IA
* **Prompt (Prompt IA 1 adaptado):**
  > Actúa como arquitecto de software experto en el modelo C4 y en Structurizr DSL. Contexto: Adjunto `inventario.md`, `001-estilo-arquitectonico.md` (Monolito Modular para San Camilo en Línea), `drivers.md` y `despliegue.py`. Tarea: escribe un workspace de Structurizr DSL con personas, el sistema, sus contenedores (con tecnología), los componentes del contenedor API, los sistemas externos (con la etiqueta "Externo") y relaciones con descripción y protocolo. Restricciones: usa SOLO las tecnologías del ADR-001 y `despliegue.py`; no confundas contenedor C4 con contenedor Docker; usa `!identifiers hierarchical`.
* **Propuesta de la IA:** Generó un primer borrador de `workspace.dsl` donde incluyó a `Nginx Proxy` y `Grafana` como contenedores de negocio del Nivel 2, y puso a `WhatsApp Business API` dentro del bloque `softwareSystem "San Camilo en Línea"`.
* **Verificación del equipo:** Se revisó con la guía del Paso 2 (Tabla 7). `WhatsApp Business API` es un sistema externo que no construimos; además, `Nginx` es infraestructura de red del VPS y no un contenedor de aplicación del MVP de 1 mes.
* **Decisión:** **Corregida.** Se movió `WhatsApp Business API` fuera del sistema con el tag `"Externo"`, y se trasladó `Nginx` a la descripción del nodo de despliegue en `deploymentEnvironment "Producción"`, dejando en Nivel 2 únicamente los 5 contenedores reales (`PWA`, `Backend API`, `Worker Celery`, `PostgreSQL` y `Redis`).

---

### Interacción 2: Modelado de Componentes (Nivel 3) y detección de discrepancia entre Lab 04 y Lab 05
* **Fecha:** 2026-10-14
* **Herramienta:** Gemini / Asistente IA
* **Prompt:**
  > Revisa nuestro `001-estilo-arquitectonico.md` (Lab 04) frente a `paquetes.puml` (Lab 05) para generar los componentes de `sancamilo.api` en `workspace.dsl`. Verifica que no existan ciclos de dependencia.
* **Propuesta de la IA:** La IA advirtió que el texto del `ADR-001` mencionaba el módulo *"Envíos"*, mientras que el diagrama `paquetes.puml` del Lab 05 definía los paquetes `catalogo`, `pedidos`, `pagos`, `notificaciones`, `reportes` y `compartido`. Propuso usar los 6 paquetes de `paquetes.puml` y actualizar el texto del `ADR-001`.
* **Verificación del equipo:** Confirmamos que en el Lab 05 la gestión de estado de entrega quedó integrada dentro de `pedidos` y se añadieron `reportes` (solo lectura) y `compartido`.
* **Decisión:** **Aceptada y aplicada.** Se actualizaron los módulos listados en `docs/architecture/adr/001-estilo-arquitectonico.md` para mantener trazabilidad 1:1 con `paquetes.puml` y con la vista `component` de `workspace.dsl`, verificando que `pagos` no dependa de `pedidos`.

---

### Interacción 3: Traducción del Diagrama de Secuencia UML a Vista Dinámica C4 (E4)
* **Fecha:** 2026-10-15
* **Herramienta:** Gemini / Asistente IA
* **Prompt:**
  > A partir de `secuencia-confirmar-pagar.puml`, genera la vista `dynamic sancamilo.api "ConfirmarYPagar"` en Structurizr DSL. Asegúrate de que cada paso utilice únicamente relaciones estáticas ya declaradas en el bloque `model`.
* **Propuesta de la IA:** En su primer intento, la IA incluyó un paso `sancamilo.api.pedidos -> yape "Cobra con Yape"` y un bloque condicional `alt` dentro de la vista `dynamic`.
* **Verificación del equipo:** Al pasar `structurizr validate`, falló porque `alt` no es sintaxis válida en Structurizr DSL y porque quien se relaciona con `yape` en el modelo estático es `sancamilo.api.pagos` (mediante `PasarelaPago`), no `pedidos` directamente.
* **Decisión:** **Corregida.** Se eliminó la sintaxis UML y se enrutó el cobro correctamente en dos pasos: `sancamilo.api.pedidos -> sancamilo.api.pagos` y `sancamilo.api.pagos -> yape`, pasando la validación sin errores.

---

### Interacción 4: Estructuración del Entorno de Despliegue según Restricciones R-03 y R-04 (E5)
* **Fecha:** 2026-10-15
* **Herramienta:** Gemini / Asistente IA
* **Prompt:**
  > Genera el bloque `deploymentEnvironment "Producción"` para `workspace.dsl` basándote en `despliegue.py` y en las restricciones R-03 (VPS único económico) y R-04 (dispositivos móviles gama baja con red 3G) de `drivers.md`.
* **Propuesta de la IA:** Inicialmente propuso desplegar la base de datos en `AWS RDS` y la aplicación en un clúster `AWS ECS Fargate`.
* **Verificación del equipo:** Esto contradecía directamente la restricción `R-03` de `drivers.md` (*"servidor VPS económico de un solo nodo para el MVP"*) y `despliegue.py`.
* **Decisión:** **Rechazada y corregida.** Se reemplazó por un nodo `Servidor VPS en la Nube (Único Nodo - R-03)` con `Ubuntu 24.04 LTS (2 vCPU, 4 GB RAM)` que aloja un nodo hijo `Docker Compose` con las instancias de `api`, `worker`, `db` y `cola`, más el nodo del dispositivo móvil del usuario para la `pwa`.

---

### Interacción 5: Auditoría de las 5 vistas exportadas con la lista oficial C4 (Prompt IA 2 - E7)
* **Fecha:** 2026-10-16
* **Herramienta:** Gemini / Asistente IA
* **Prompt (Prompt IA 2 de la guía):**
  > Actúa como revisor de diagramas de arquitectura. Evalúa estas vistas exportadas de un modelo C4 [se adjuntaron los 5 archivos `.puml` de `export/`] con la lista de revisión de c4model.com: generales, elementos y relaciones. Responde en una tabla (vista, pregunta de la lista, cumple sí/no, evidencia, corrección sugerida). No inventes problemas: si algo cumple, indícalo.
* **Propuesta de la IA:** Confirmó el cumplimiento de títulos, leyendas, tecnologías y formas, pero señaló como supuestos defectos que en la vista de Contexto faltaban protocolos `[HTTPS]` en las flechas de las Personas y que en Componentes las llamadas internas no indicaban protocolo HTTP/REST.
* **Verificación del equipo:** Contrastamos ambos puntos con la teoría de Simon Brown (`c4model.com`) y el `ADR-001`: en Nivel 1 no se colocan protocolos técnicos en las relaciones de usuario, y en un Monolito Modular los componentes se invocan en memoria dentro del mismo proceso Python.
* **Decisión:** **Documentados como Falsos Positivos en `revision-c4.md`.** Se conservaron las vistas tal como estaban por ser arquitectónicamente correctas.

---

### Interacción 6: Redacción del resumen para público no técnico (Prompt IA 3 - E7)
* **Fecha:** 2026-10-16
* **Herramienta:** Gemini / Asistente IA
* **Prompt (Prompt IA 3 adaptado):**
  > Explica el siguiente diagrama de contexto al presidente de la Junta de Comerciantes del Mercado San Camilo, que no es técnico, en máximo 120 palabras: qué hace el sistema, quién lo usa y de qué servicios externos depende. Evita la jerga técnica. [Se adjuntó `Structurizr-Contexto.puml`].
* **Propuesta de la IA:** Redactó un texto claro de 115 palabras, pero mencionaba que el sistema *"también acepta pagos con Plin y tarjetas de crédito"*.
* **Verificación del equipo:** Aunque Plin aparece en `drivers.md` como escenario futuro de modificabilidad (QA-03), en el MVP actual y en el modelo C4 solo está integrada la pasarela **Yape** (RF-03).
* **Decisión:** **Corregida.** Se editó `explicacion.md` dejando únicamente **Yape** y **WhatsApp** para que el texto (108 palabras) sea 100% fiel al modelo C4 construido.