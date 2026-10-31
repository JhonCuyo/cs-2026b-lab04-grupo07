# ADR-006: Índice Compuesto en PostgreSQL y Caché en Redis para el Catálogo Multimercado

* **Estado:** Aceptado
* **Fecha:** 2026-10-28
* **Decisores:** Grupo 07 (San Camilo en Línea)

## Contexto
Con la incorporación de los mercados **Altiplano** y **Río Seco** al Mercado San Camilo (`QA-03`), la carga en hora punta dominical sube a **18 req/s**. En la simulación de colas $M/G/c$ (`fitness/rendimiento.py`) con los 4 workers actuales y sin tácticas, la base de datos se satura y el tiempo de respuesta `p95` se dispara a **21 480,5 ms (21,5 s)**, incumpliendo el presupuesto máximo de **1500 ms**.

## Alternativas Consideradas
1. **Escalar a 8 workers contratando un segundo VPS:** Baja el `p95` a 641,8 ms, pero duplica el costo mensual de infraestructura violando `R-03`.
2. **Solo Caché en Redis (TTL 30 s):** Logra 342,1 ms con 85% de aciertos, pero presenta un punto de sensibilidad severo: cuando la tasa de aciertos baja del 20% (caché fría), el `p95` supera los 3500 ms.
3. **Índice compuesto `(mercado_id, puesto_id)` en PostgreSQL + Caché en Redis con TTL de 30 s (Opción elegida):** Combina optimización en base de datos y reducción de demanda.

## Decisión
Adoptamos un **índice compuesto `(mercado_id, puesto_id)`** en la tabla de productos/catálogo de PostgreSQL 16 junto con una **caché *cache-aside* en Redis con TTL de 30 segundos** particionada por mercado. No se escala a un segundo VPS en esta etapa.

## Consecuencias
* **Positivas (Evidencia):** El `p95` a 18 req/s cae a **115,3 ms** (y a **184,2 ms** incluso con 0% de aciertos en caché), manteniendo el costo en un solo VPS.
* **Negativas / Trade-off aceptado:** Posible desfase de hasta 30 segundos en la visualización del stock (`Riesgo R4`), mitigado validando el stock de forma transaccional al confirmar el pedido en `Módulo Pedidos`.