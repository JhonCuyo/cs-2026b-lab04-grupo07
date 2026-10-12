# Auditoría de Consistencia de Diagramas UML (Reglas C1-C5)

En esta sección se consolidan los hallazgos reportados por la herramienta de IA generativa (Prompt IA 3 - Auditor de consistencia) al revisar los cinco diagramas del sistema **San Camilo en Línea** (`clases.puml`, `secuencia-confirmar-pagar.puml`, `estados-pedido.mmd`, `actividades-preparacion-pedido.puml` y `paquetes.puml`).

## Tabla de Hallazgos y Verificación del Equipo

| Regla | Elemento / Diagrama | Hallazgo Reportado por la IA | Verificación del Equipo y Decisión | Estado |
|---|---|---|---|---|
| **C1** | `secuencia-confirmar-pagar.puml` | El mensaje `notificarNuevoPedido(pedido)` enviado a `Notificador` no existe como método en `Comprador`. | **Falso Positivo de la IA:** El mensaje va dirigido a la interfaz `Notificador`, donde sí está declarado el método `notificarNuevoPedido()`. La IA confundió la línea de vida receptora. | **Rechazado** (Falso positivo identificado) |
| **C2** | `estados-pedido.mmd` | La transición hacia el estado `RECOGIDO` usa `recogerPedido()`, la cual no figuraba originalmente en `PedidoPuesto`. | **Hallazgo Válido:** Se procedió a incluir la operación `recogerPedido()` dentro de la clase `PedidoPuesto` en `clases.puml` para mantener coincidencia 1 a 1. | **Corregido** |
| **C3** | `clases.puml` | La relación entre `PedidoMultipuesto` y `LineaPedido` figura sin restricción explícita de mínimo 1 elemento en el código Python. | **Hallazgo Válido:** En el diagrama de clases se indicó `1 *-- 1..*` y en la implementación Python de `confirmar()` se agregó la validación que lanza `ValueError` si las líneas están vacías. | **Verificado y Mitigado** |
| **C4** | `paquetes.puml` | El paquete `pagos` depende directamente de `pedidos`, generando un posible ciclo. | **Falso Positivo de la IA:** La IA leyó erróneamente el sentido de la flecha de dependencia. La relación real es `PED ..> PAG` a través del puerto `PasarelaPago`. El paquete `pagos` no conoce a `pedidos`. | **Rechazado** (Falso positivo identificado) |
| **C5** | `clases.puml` / `dominio.py` | Inconsistencia de nombres entre `calcularTotal` (diagrama) y `calcular_total` (código fuente). | **Diferencia Convencional:** Es una adaptación válida de nomenclatura (`camelCase` para modelado UML y `snake_case` para el estándar PEP 8 de Python). Se documenta la equivalencia. | **Aceptado y Documentado** |