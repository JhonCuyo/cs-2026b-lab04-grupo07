# Iteración 2 de ADD 3.0 — Rendimiento en Hora Punta Tri-Mercado (`QA-03`)

## 1. Objetivo de la Iteración
Cumplir el escenario **`QA-03 (H, M)`**: Soportar **18 req/s** de consultas al catálogo durante la hora punta dominical de los 3 mercados (**San Camilo, Altiplano y Río Seco**) manteniendo una latencia **p95 $\le 1500$ ms** sin exceder el presupuesto del VPS único (`R-03`).

## 2. Elementos a Refinar
* Contenedor **Base de Datos (`PostgreSQL 16`)**: Índices de búsqueda por mercado y puesto.
* Contenedor **Cola y Caché (`Redis`)**: Caché de lecturas del catálogo particionada por clave `catalogo:{mercado_id}:{puesto_id}`.
* Contenedor **Backend API (`Módulo Catálogo`)**: Lectura *cache-aside* con TTL de 30 segundos.

## 3. Conceptos de Diseño Evaluados

| Concepto de Diseño | Táctica (Bass et al.) | Qué Mejora | Trade-off (Qué Empeora) | Decisión del Equipo |
| :--- | :--- | :--- | :--- | :--- |
| **Migrar el módulo Catálogo a un microservicio en Go con Kubernetes** | Escalar / Descomponer | Latencia extrema | Rompe el plazo de 1 mes (`R-01`) y el presupuesto de 1 VPS (`R-03`). | **Rechazada:** Sobreingeniería innecesaria según la simulación. |
| **Duplicar el VPS (de 4 a 8 workers Gunicorn)** | Aumentar recursos | Baja el `p95` a 18 req/s de 21,4 s a 640 ms | Duplica el costo mensual de infraestructura en la nube. | **Plan de contingencia (No adoptada aún):** El índice + caché logran mejor resultado sin costo extra. |
| **Índice compuesto `idx_productos_mercado_puesto` en PostgreSQL** | Gestionar recursos: *Optimizar consultas* | Reduce el tiempo medio de consulta en BD de ~240 ms a ~42 ms | Penalización mínima en escrituras (`INSERT`/`UPDATE`) y ~15 MB de disco. | **Aceptada (`ADR-006`).** |
| **Caché de catálogo en Redis con TTL de 30 s** | Controlar demanda: *Caché* | Reduce las lecturas recurrentes a ~4 ms y descarga la BD en un 85% | Puede mostrar stock con hasta 30 s de desfase (Riesgo `R4`). | **Aceptada (`ADR-006`) combinada con el índice.** |

## 4. Evidencia Cuantitativa (`fitness/rendimiento.py` — Simulación $M/G/c$)
Supuestos de la simulación: Llegadas de Poisson ($\lambda = 6, 12, 18\text{ req/s}$), $c = 4$ workers en el VPS, tiempos de servicio lognormales (240 ms sin índice, 42 ms con índice, 4 ms en acierto de Redis) durante 120 segundos:

| Configuración Evaluada | Normal (`6 req/s`) `p95` | 1 Mercado Pico (`12 req/s`) `p95` | 3 Mercados Pico (`18 req/s`) `p95` | ¿Cumple `QA-03` ($\le 1500\text{ ms}$)? |
| :--- | :---: | :---: | :---: | :---: |
| **Sin tácticas (4 workers, BD sin índice)** | 685,4 ms | 1492,0 ms | **21 480,5 ms (Colapso)** | **NO** |
| **Escalar a 8 workers (2 VPS, sin índice)** | 560,2 ms | 582,1 ms | **641,8 ms** | Sí (pero duplica costo) |
| **Solo Caché Redis (85% hit rate, sin índice)** | 310,5 ms | 328,4 ms | **342,1 ms** *(Falla si hit rate $< 20\%$)* | Parcial (sensible a caché fría) |
| **Solo Índice compuesto en PostgreSQL** | 112,3 ms | 134,6 ms | **184,2 ms** | **SÍ** |
| **Índice compuesto + Caché Redis 85% (Adoptada)** | **78,4 ms** | **92,1 ms** | **115,3 ms** | **SÍ (Con amplio margen)** |

Ver gráfico generado en: `docs/architecture/add/rendimiento_iteracion2.png`.