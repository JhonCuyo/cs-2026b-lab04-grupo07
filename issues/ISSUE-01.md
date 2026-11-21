# Issue #01: Un pedido a varios puestos cobra dos veces la comisión

**Reportado por:** administración del Mercado San Camilo  
**Observado:** Cuando un cliente arma un carrito con productos de 2 puestos distintos (por ejemplo, Puesto A-12 y Puesto B-05), `calcular_comision_pedido()` cobra S/ 5.00 (dos veces la comisión fija de S/ 2.50). Con 3 puestos cobra S/ 7.50.  
**Esperado:** Un pedido multipuesto debe cobrar una única comisión fija de S/ 2.50 (`COMISION_FIJA_PEDIDO`) independientemente de la cantidad de puestos, y S/ 0.00 si la lista de ítems está vacía.  
**Prueba que reproduce el error:** `tests/test_issue_01_comision.py::test_issue_01_pedido_multipuesto_cobra_una_sola_comision`
