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