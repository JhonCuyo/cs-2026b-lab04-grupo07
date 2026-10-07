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