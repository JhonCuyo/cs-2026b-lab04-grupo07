    # Iteración 3 de ADD 3.0 — Disponibilidad ante Caídas de Pasarela y Red 3G (`QA-04` y `QA-05`)

## 1. Objetivo de la Iteración
Atender los escenarios de disponibilidad:
* **QA-04 (H, H):** Si la pasarela de pagos (Yape/Plin) sufre una caída total de 20 minutos además de 8% de fallas transitorias en una jornada de 1800 pedidos, el sistema debe registrar **0 pedidos perdidos** y realizar **$\le 20$ llamadas** al proveedor durante su caída.
* **QA-05 (H, M):** Si un comerciante en el interior de San Camilo, Altiplano o Río Seco pierde señal 3G al actualizar su catálogo, la PWA debe guardar los cambios localmente y sincronizarlos en **$\le 3$ minutos** al recuperar conexión.

## 2. Elementos a Refinar
* **Módulo Pagos (`src/pedidos/pagos.py` y `fitness/disponibilidad.py`):** Incorporación del decorador `ConCircuitBreaker` sobre el puerto `PasarelaPago` (Lab 07).
* **Base de Datos (`PostgreSQL 16`) y `Worker Celery`:** Tabla transaccional `outbox_pagos` para persistir cobros diferidos cuando el circuito está abierto (mitigando el Riesgo `R3` detectado en ATAM-lite).
* **Contenedor `PWA San Camilo`:** Almacenamiento local en `IndexedDB` + `Background Sync API` del Service Worker (`QA-05`).

## 3. Conceptos de Diseño Evaluados

| Concepto de Diseño | Táctica (Bass et al.) | Qué Mejora | Trade-off (Qué Empeora) | Decisión del Equipo |
| :--- | :--- | :--- | :--- | :--- |
| **Solo Reintentos Síncronos (`ConReintentos`, 3 intentos)** | Recuperarse de fallas: *Reintentos* | Cubre el 8% de micro-cortes transitorios de red 3G | Durante la caída de 20 min pierde los 60 pedidos y bombardea al proveedor caído con **180 llamadas**. | **Insuficiente por sí sola:** Se mantiene solo para fallas transitorias, envuelta por el Circuit Breaker. |
| **Guardar pagos pendientes únicamente en una lista de Redis** *(Propuesta inicial de IA)* | Cola en memoria | Rápida de encolar | Si el contenedor Redis se reinicia, se pierden los pagos pendientes (**Riesgo R3**). | **Rechazada:** El dinero/pedidos confirmados exigen durabilidad ACID. |
| **Reintentos + `ConCircuitBreaker` (umbral=3, espera=120s) + Tabla `outbox_pagos` en PostgreSQL** | Prevenir y recuperarse de fallas: *Circuit Breaker + Outbox* | **0 pedidos perdidos** y reduce de 180 a **18** las llamadas durante la caída de 20 min. | Consistencia eventual: el cobro se liquida cuando el worker procesa el outbox. | **Aceptada (`ADR-007`).** |
| **PWA Offline-first con `IndexedDB` + `Service Worker`** | Prevenir fallas en cliente: *Offline-first* | El comerciante publica/edita productos sin señal 3G (`R-04`). | Posibles colisiones si dos celulares editan el mismo puesto desconectados (resuelto con LWW). | **Aceptada (`ADR-007`).** |

## 4. Evidencia Cuantitativa (`fitness/disponibilidad.py` — Simulación Monte Carlo de 1800 pedidos)

| Estrategia Evaluada | Pedidos Totales | Completados al Finalizar Jornada | Pedidos Perdidos | Llamadas al Proveedor durante Caída de 20 min | ¿Cumple `QA-04`? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Sin tácticas** | 1800 | 1605 (89,2%) | 195 perdidos | 60 llamadas | **NO** |
| **Solo Reintentos (3 intentos)** | 1800 | 1740 (96,7%) | 60 perdidos | 180 llamadas (Sobrecarga) | **NO** |
| **Reintentos + Circuit Breaker + Outbox PostgreSQL (Adoptada)** | **1800** | **1800 (100,0%)** *(1740 directos + 60 vía Outbox)* | **0 perdidos** | **18 llamadas** (Reducción del 90%) | **SÍ** |

Ver gráfico generado en: `docs/architecture/add/disponibilidad_iteracion3.png`.