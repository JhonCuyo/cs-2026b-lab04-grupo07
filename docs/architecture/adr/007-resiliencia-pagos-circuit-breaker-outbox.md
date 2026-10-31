# ADR-007: Reintentos, Circuit Breaker, Tabla Outbox en PostgreSQL y PWA Offline-first

* **Estado:** Aceptado
* **Fecha:** 2026-10-28
* **Decisores:** Grupo 07 (San Camilo en Línea)

## Contexto
El escenario `QA-04 (H, H)` exige **0 pedidos perdidos** y **$\le 20$ llamadas** al proveedor cuando la pasarela externa Yape/Plin sufre una caída de 20 minutos además de un 8% de fallas transitorias en una jornada de 1800 pedidos. Asimismo, `QA-05 (H, M)` requiere que los comerciantes en puestos interiores sin señal 3G (`R-04`) puedan registrar stock sin perder cambios.

## Alternativas Consideradas
1. **Solo Reintentos síncronos (`ConReintentos`, 3 intentos):** Cubre fallas transitorias pero pierde **60 pedidos** durante la caída de 20 minutos y realiza **180 llamadas** inútiles al proveedor caído.
2. **Encolar pagos pendientes únicamente en Redis (Propuesta inicial de IA):** Descartada porque un reinicio de Redis sin persistencia provocaría la pérdida de cobros confirmados (`Riesgo R3`).
3. **Reintentos + `ConCircuitBreaker` (Decorator) + Tabla `outbox_pagos` en PostgreSQL + PWA Offline-first con `IndexedDB` (Opción elegida).**

## Decisión
Envolvemos el puerto `PasarelaPago` (Lab 07) con el decorador `ConCircuitBreaker` (`umbral=3` fallas, `espera_s=120`). Cuando el circuito se abre, el pedido se guarda de forma atómica en una tabla `outbox_pagos` en PostgreSQL 16, que el `Worker de Tareas (Celery)` procesa en segundo plano. En el frontend, la `PWA San Camilo` almacena cambios de catálogo en `IndexedDB` y los sincroniza mediante `Service Worker` al detectar señal (`QA-05`).

## Consecuencias
* **Positivas (Evidencia):** La simulación Monte Carlo (`fitness/disponibilidad.py`) demuestra **0 pedidos perdidos (100% completados)** y reduce de **180 a 18** las llamadas al proveedor caído.
* **Negativas / Trade-off aceptado:** Consistencia eventual durante caídas prolongadas de la pasarela (el pago y el aviso de WhatsApp al comerciante se confirman de forma diferida).