# Análisis de No Determinismo en Modelos de Lenguaje (E7.2)

Se ejecutó el prompt `v3.txt` tres veces consecutivas sobre tres casos de prueba representativos (`caso_1`, `caso_5` y `caso_8`).

## Resultados de las 3 Ejecuciones
* **Variabilidad semántica menor:** Variaciones en unidades (ej. *Kg* vs *Kilo*) justifican aserciones flexibles basadas en subcadenas.
* **Variabilidad en flotantes:** Los valores de confianza varían levemente, requiriendo validar rangos en lugar de valores exactos.
* **Conclusión:** Justifica plenamente el uso de **proveedores grabados (fixtures)** en las pruebas unitarias de CI para garantizar determinismo absoluto.