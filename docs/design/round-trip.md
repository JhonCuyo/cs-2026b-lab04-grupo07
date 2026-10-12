# Análisis de Comparación Round-Trip (E6)

En esta fase se compara el diagrama de diseño original (`clases.puml`) con el diagrama generado automáticamente mediante ingeniería inversa (`classes_pedidos_reverse.puml`) a partir del código fuente en Python (`src/pedidos/dominio.py`).

## Tabla Comparativa de Diferencias

| N° | Diferencia Observada | Causa | Acción Tomada |
|---|---|---|---|
| 1 | **Ausencia de composiciones explicitas** entre `PedidoMultipuesto` y `LineaPedido` / `PedidoPuesto`. | `pyreverse` no deduce la relación de composición UML a partir de atributos de tipo colección (`list[...]`). | **Documentar limitación:** Se mantiene la composición explícita (`1 *-- 1..*`) en el diagrama de diseño, ya que representa adecuadamente la regla de dominio. |
| 2 | **Falta de multiplicidades** en todas las asociaciones del diagrama inverso. | El lenguaje Python y los *type hints* estándar no expresan límites numéricos de cardinalidad/multiplicidad. | **Validación en código (Regla C3):** Se agregó una validación explícita en `PedidoMultipuesto.confirmar()` para garantizar que exista al menos una línea (`1..*`). |
| 3 | **Convención de nomenclatura (`camelCase` vs `snake_case`)**. | El diagrama usa `camelCase` por estándares UML de diseño, mientras que el código implementa `snake_case` siguiendo PEP 8 de Python. | **Aceptar equivalencia (Regla C5):** Se documenta la equivalencia funcional de los nombres (`calcularTotal()` == `calcular_total()`). |
| 4 | **Representación de Interfaz `PasarelaPago`**. | En el diagrama inverso figura como una clase estándar con método abstracto, no con el estereotipo `<<puerto>>` o `<<interface>>`. | **Aceptable:** Python no posee la palabra clave `interface` y las implementa mediante `ABC` y `@abstractmethod`. |