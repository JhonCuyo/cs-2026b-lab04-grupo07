# Issue #03: Error de redondeo en céntimos al calcular totales

**Reportado por:** tesorería y conciliación Yape  
**Observado:** Al calcular totales con precios que terminan en mitades de céntimo o sumas binarias inexactas (como `1.005` o `2.675` con `float`), `calcular_total_soles()` produce diferencias de S/ 0.01 respecto al redondeo comercial estándar (`ROUND_HALF_UP`).  
**Esperado:** El cálculo debe realizarse con `decimal.Decimal` y redondear a `"0.01"` usando `ROUND_HALF_UP`.  
**Prueba que reproduce el error:** `tests/test_issue_03_redondeo.py::test_issue_03_redondeo_exacto_en_centimos`
