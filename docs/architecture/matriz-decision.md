# Matriz de Decisión - San Camilo en Línea

## Alternativas Consideradas
* **A. Monolito en Capas:** Estructura tradicional dividida en Presentación, Lógica de Negocio y Acceso a Datos. Despliegue en una única unidad executable.
* **B. Monolito Modular:** Sistema desplegado como una sola unidad pero dividido internamente en módulos independientes por dominio (Catálogo, Pedidos, Pagos, Notificaciones), comunicados mediante interfaces explícitas.
* **C. Microservicios:** Múltiples servicios independientes por dominio, cada uno con su propia base de datos, desplegados sobre contenedores y comunicados vía API Gateway/Broker.

## Criterios de Evaluación y Pesos
| Criterio | Peso | Justificación (Driver relacionado) |
|---|---|---|
| Tiempo de Entrega | 25% | R-01: Obligatoriedad de lanzar el MVP en producción en máximo 1 mes. |
| Costo Operativo | 25% | R-03: Presupuesto limitado; requiere funcionar en un único servidor VPS económico. |
| Usabilidad y Rendimiento Móvil | 20% | QA-01 y QA-02: Publicación en $\le 3$ toques y carga optimizada en redes 3G. |
| Modificabilidad | 15% | QA-03: Facilidad para integrar nuevas pasarelas o servicios sin tocar otros módulos. |
| Simplicidad Operativa | 15% | R-02: Equipo de 3 desarrolladores sin experiencia avanzada en DevOps/Kubernetes. |

## Matriz de Evaluación (Puntaje 1: Muy malo | 5: Excelente)
| Criterio (Peso) | A. Monolito en Capas | B. Monolito Modular | C. Microservicios |
|---|---|---|---|
| Tiempo de Entrega (25%) | 5 | 4 | 2 |
| Costo Operativo (25%) | 5 | 5 | 2 |
| Usabilidad y Rendimiento Móvil (20%) | 3 | 4 | 4 |
| Modificabilidad (15%) | 2 | 4 | 5 |
| Simplicidad Operativa (15%) | 5 | 4 | 1 |
| **Total Ponderado** | **4.20** | **4.25** | **2.60** |

*Cálculos de Total Ponderado:*
* **A. Monolito en Capas:** $(0.25 \times 5) + (0.25 \times 5) + (0.20 \times 3) + (0.15 \times 2) + (0.15 \times 5) = 1.25 + 1.25 + 0.60 + 0.30 + 0.75 = \mathbf{4.20}$
* **B. Monolito Modular:** $(0.25 \times 4) + (0.25 \times 5) + (0.20 \times 4) + (0.15 \times 4) + (0.15 \times 4) = 1.00 + 1.25 + 0.80 + 0.60 + 0.60 = \mathbf{4.25}$
* **C. Microservicios:** $(0.25 \times 2) + (0.25 \times 2) + (0.20 \times 4) + (0.15 \times 5) + (0.15 \times 1) = 0.50 + 0.50 + 0.80 + 0.75 + 0.15 = \mathbf{2.60}$

## Conclusión
Elegimos la **Alternativa B: Monolito Modular** (puntaje total: 4.25). Ofrece un equilibrio ideal entre rapidez de desarrollo y bajo costo operativo (necesarios para el MVP en 1 mes), manteniendo al mismo tiempo un alto grado de modificabilidad y aislamiento de responsabilidades. La opción de microservicios fue descartada por su alta complejidad de despliegue y sobrecosto de infraestructura. Ver detalles en [ADR-001](adr/001-estilo-arquitectonico.md).