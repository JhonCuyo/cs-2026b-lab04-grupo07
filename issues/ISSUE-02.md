# Issue #02: Producto agotado sigue visible en el catálogo

**Reportado por:** comerciantes del pabellón de frutas y verduras  
**Observado:** `listar_productos_visibles()` devuelve productos con `stock == 0` o negativo siempre que `activo=True`, lo que provoca pedidos fallidos al intentar reservar stock.  
**Esperado:** Solo deben aparecer visibles los productos con `activo is True` y `stock > 0`.  
**Prueba que reproduce el error:** `tests/test_issue_02_agotados.py::test_issue_02_producto_agotado_no_es_visible`
