# Bitácora de Uso de IA — Laboratorio 08 (Diseño Guiado por Atributos de Calidad, ADD y ATAM-lite)

Registro auditable bajo la regla de oro: *"La IA propone, el equipo decide con evidencia cuantitativa"*.

---

### Interacción 1: Generación y priorización del Árbol de Utilidad (Prompt IA 1 — E1)
* **Fecha:** 2026-10-27
* **Herramienta:** Gemini / Asistente IA
* **Prompt:**
  > Actúa como arquitecto de software. Contexto: Adjunto `drivers.md`, `ADR-001` (Monolito Modular) y el nuevo escenario de crecimiento del Caso 7: se suman los mercados Altiplano y Río Seco a San Camilo, cada uno con sus reglas y comerciantes, llegando a 18 req/s en hora punta. Tarea: propón escenarios de calidad de seis partes para rendimiento, disponibilidad, seguridad y modificabilidad con calificación (Importancia, Dificultad) en H/M/L.
* **Propuesta de la IA:** Propuso 7 escenarios, pero calificó `QA-06` (agregar una nueva pasarela de pago) y `QA-07` (cifrado de datos personales) con dificultad alta `(H, H)`.
* **Verificación del equipo:** Revisamos contra nuestro estado actual del repositorio (Labs 04 a 07): `QA-06` ya fue resuelto en el Lab 07 mediante los patrones `Strategy + Adapter + Factory` (`ADR-005`), y `QA-07` ya está cubierto por Nginx con TLS en `despliegue.py`.
* **Decisión:** **Corregida.** Se bajaron `QA-06` y `QA-07` a `(M, L)` y se priorizaron como `(H, H)` y `(H, M)` los escenarios `QA-01` (aislamiento multimercado), `QA-02` (reglas por mercado en BD), `QA-03` (18 req/s) y `QA-04`/`QA-05` (resiliencia ante caída de Yape y red 3G).

---

### Interacción 2: Selección de tácticas para Aislamiento y Modificabilidad Multimercado (Iteración 1 — E2)
* **Fecha:** 2026-10-27
* **Herramienta:** Gemini / Asistente IA
* **Prompt (Prompt IA 2 adaptado):**
  > Para los escenarios `QA-01` (0 filas filtradas entre San Camilo, Altiplano y Río Seco) y `QA-02` (incorporar un mercado con sus propias tarifas en <= 1 día sin desplegar código), propón 4 conceptos de diseño respetando el `ADR-001` (Monolito Modular en un solo VPS).
* **Propuesta de la IA:** Sugirió como primera opción desplegar un contenedor PostgreSQL y una instancia de Django separada por cada mercado, y como tercera opción usar `Row-Level Security (RLS)` con tabla de configuración.
* **Verificación del equipo:** Levantar 3 bases de datos PostgreSQL y 3 backends consume más de los 4 GB de RAM de nuestro VPS único (`R-03`) y exige modificar el `docker-compose.yml` cada vez que entra un mercado nuevo.
* **Decisión:** **Rechazada la opción de múltiples BDs; aceptada la combinación de `mercado_id` + RLS en PostgreSQL + tabla `ConfiguracionMercado` (`ADR-008`),** verificada con el prototipo `fitness/aislamiento_modificabilidad.py`.

---

### Interacción 3: Simulación de rendimiento y curva de sensibilidad de la caché (Iteración 2 — E4)
* **Fecha:** 2026-10-28
* **Herramienta:** Gemini / Asistente IA
* **Prompt:**
  > Evalúa qué tácticas necesitamos para cumplir `QA-03` (`p95 <= 1500 ms` a 18 req/s en los 3 mercados). La IA afirmó inicialmente que *"basta con poner Redis delante de la base de datos sin tocar las tablas de PostgreSQL, porque la caché siempre mantiene el p95 por debajo de 400 ms"*.
* **Propuesta de la IA:** Confiar exclusivamente en la caché de Redis sin crear índices compuestos en PostgreSQL.
* **Verificación con evidencia (`fitness/rendimiento.py`):** Trazamos la curva de sensibilidad variando la tasa de aciertos (*hit rate*) de 0% a 95% a 18 req/s. Descubrimos que cuando la caché está fría o tiene menos de 20% de aciertos (por ejemplo, al iniciar la hora punta o tras expirar las claves), el `p95` con *solo caché* sube a **más de 3500 ms**, violando `QA-03`. En cambio, al agregar el índice compuesto `(mercado_id, puesto_id)`, incluso con **0% de caché** el `p95` es **184,2 ms**.
* **Decisión:** **Corregida la afirmación de la IA con evidencia.** Se adoptaron ambas tácticas en conjunto (`Índice compuesto + Caché Redis TTL 30 s`, `ADR-006`), logrando `p95 = 115,3 ms`.

---

### Interacción 4: Ubicación de la cola de pagos pendientes cuando se abre el Circuit Breaker (Iteración 3 — E4)
* **Fecha:** 2026-10-28
* **Herramienta:** Gemini / Asistente IA
* **Prompt:**
  > Diseña la táctica de resiliencia sobre el puerto `PasarelaPago` para lograr 0 pedidos perdidos durante una caída de 20 minutos de Yape (`QA-04`).
* **Propuesta de la IA:** Propuso el decorador `ConCircuitBreaker`, pero cuando el circuito estaba `ABIERTO` guardaba los cobros pendientes en una lista volátil en memoria dentro de Redis (`LPUSH pagos_pendientes`).
* **Verificación del equipo:** Analizamos los modos de falla: si el contenedor de Redis se reinicia por falta de memoria o mantenimiento durante la caída, todos los cobros diferidos se pierden, incumpliendo `QA-04`.
* **Decisión:** **Corregida (`Riesgo R3` mitigado).** Los cobros diferidos se insertan dentro de la misma transacción ACID en la tabla `outbox_pagos` de PostgreSQL (`ADR-007`), logrando 0 pedidos perdidos y solo 18 llamadas en la simulación Monte Carlo (`fitness/disponibilidad.py`).

---

### Interacción 5: Evaluador adversario ATAM-lite y refutación de falso positivo sobre Celery (Prompt IA 3 — E3/E7)
* **Fecha:** 2026-10-29
* **Herramienta:** Gemini / Asistente IA
* **Prompt (Prompt IA 3):**
  > Actúa como evaluador ATAM escéptico. Te paso el árbol de utilidad, los ADR-006 a 008, la vista de contenedores y los resultados de las simulaciones. Identifica puntos de sensibilidad, trade-offs, riesgos y no riesgos.
* **Propuesta de la IA:** Identificó correctamente los puntos de sensibilidad y los riesgos `R1` a `R4`, pero además reportó como "Riesgo Crítico" que *"el worker de Celery colapsará en la campaña de los 3 mercados y deben reemplazarlo por un clúster de Apache Kafka"*.
* **Verificación con evidencia:** Calculamos la tasa real de eventos asíncronos de pago: 1800 pedidos en una jornada de 10 horas equivalen a **3 pedidos por minuto (0,05 tareas/segundo)**. Un único proceso worker de Celery en Python procesa hasta 50 tareas simples por segundo.
* **Decisión:** **Rechazado como Falso Positivo en `atam-lite.md`.** Se mantiene Redis + Celery y se descarta Kafka por violar el plazo de 1 mes y la memoria del VPS.

---

### Interacción 6: Configuración de contratos de `import-linter` (`FF-01` y `FF-02` — E5)
* **Fecha:** 2026-10-29
* **Herramienta:** Gemini / Asistente IA
* **Prompt:**
  > Genera el archivo `.importlinter` para verificar que los módulos de `src.sancamilo` respeten las capas sin ciclos del `ADR-001` y que ningún módulo de negocio importe directamente `src.sancamilo.pagos.adaptadores` (`ADR-005`).
* **Propuesta de la IA:** Generó los contratos `layers` y `forbidden`, pero colocó a `reportes` en la capa inferior debajo de `pedidos`.
* **Verificación del equipo:** En nuestro diagrama de paquetes del Lab 05 (`paquetes.puml`) y en el modelo C4 del Lab 06, `reportes` depende de `pedidos` (solo lectura), por lo que en un contrato `layers` de `import-linter` `reportes` debe ir en la capa superior.
* **Decisión:** **Corregido el orden de capas en `.importlinter`** y comprobado con la prueba de violación intencional (`docs/architecture/add/violacion-fitness-prueba.md`).