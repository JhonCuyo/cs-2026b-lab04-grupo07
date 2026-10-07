# Historia de Usuario - HU-07: Pedido multipuesto con pago único

**Como** comprador del mercado San Camilo,  
**Quiero** realizar un pedido seleccionando productos de distintos puestos del mercado y pagar una sola vez con Yape o Plin,  
**Para** no realizar múltiples transferencias y recibir todo en una sola entrega.

## Criterios de Aceptación

### Criterio 1: Confirmación de pago y derivación a puestos
**Dado** un pedido multipuesto en estado `BORRADOR` con ítems de al menos dos puestos distintos y stock disponible,  
**Cuando** el comprador confirma el pedido y la pasarela aprueba el pago único (Yape o Plin),  
**Entonces** el estado del pedido cambia a `PAGADO`, se generan las órdenes por cada puesto en estado `RECIBIDO`, y se envía una notificación por WhatsApp a cada comerciante.

### Criterio 2: Rechazo de pago o falta de stock
**Dado** un pedido multipuesto confirmado,  
**Cuando** el pago es rechazado por la pasarela o la transacción excede los 15 minutos,  
**Entonces** el pedido cambia a estado `CANCELADO`, se liberan los productos reservados y se notifica al comprador.