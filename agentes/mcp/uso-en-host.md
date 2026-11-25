# Uso del servidor MCP `sancamilo` en un host real (E5)

- **Host:** VS Code + GitHub Copilot en modo agente.
- **Configuración:** `.vscode/mcp.json` (transporte `stdio`, intérprete Python del entorno virtual de Windows).
- **Servidor:** `agentes/mcp/servidor_mcp/sancamilo_mcp.py`.

## Verificación del host MCP

Se verificó el servidor `sancamilo` disponible en esta sesión de Copilot. El catálogo reportó 4 herramientas, 2 recursos, 1 plantilla de recurso y 2 prompts. Se ejecutaron las cinco consultas de la tabla a través del servidor MCP; la cuarta se comprobó solicitando el prompt y verificando su contenido renderizado.

La quinta consulta crea un borrador. Fue ejecutada con la autorización explícita del usuario para validar las cinco consultas; en esta ejecución no apareció un diálogo de aprobación independiente del host.

## Registro de consultas

| N.º | Consulta en lenguaje natural | Capacidad MCP esperada | ¿Requiere permiso? | Resultado observado |
| :-: | :--- | :--- | :---: | :--- |
| 1 | ¿Qué productos están disponibles actualmente en el puesto A-01 de San Camilo? | `buscar_producto(puesto="A-01")` | No | Correcto: Rocoto arequipeño, stock 14, S/ 5.50/kg; Cebolla roja, stock 25, S/ 3.20/kg. |
| 2 | Muéstrame el resumen de pedidos y el total en soles del puesto A-01. | `pedidos_por_puesto(puesto="A-01")` | No | Correcto: 2 pedidos (`#101` PAGADO y `#102` ENTREGADO), `total_soles: "20.60"` y `comision_fija: 2.5`. |
| 3 | Ejecuta las pruebas unitarias del proyecto para verificar que todo sigue en verde. | `ejecutar_pruebas()` | No | Correcto: `37 passed in 0.16s`. |
| 4 | Usa el prompt `oferta_del_dia` del servidor `sancamilo` para el puesto A-01 con Rocoto S/ 5.50/kg y Cebolla S/ 3.20/kg. | `oferta_del_dia(puesto="A-01", productos=...)` | No | Correcto: `get_prompt` devolvió la plantilla para A-01, con delimitadores `<productos>` y el texto de productos solicitado. El prompt pide redactar un aviso de máximo 3 líneas; el servidor entrega la plantilla, no genera por sí mismo el texto final. |
| 5 | Registra un pedido borrador para Cliente-09 en el puesto B-05 de 2 porciones de Queso helado artesanal. | `registrar_pedido_borrador(cliente="Cliente-09", puesto="B-05", producto="Queso helado artesanal (porción)", cantidad=2)` | Sí; autorizada por la solicitud explícita. No apareció un diálogo adicional. | Correcto: creó `agentes/mcp/borradores/PEDIDO-02.json` en estado `BORRADOR`; `PEDIDO-01.json` permaneció intacto. |

El borrador `PEDIDO-01.json` de E4 se conservó y la ejecución E5 creó el siguiente archivo secuencial, `PEDIDO-02.json`. La herramienta de escritura está marcada como no-lectura (`read_only_hint=False`); en esta sesión, sin embargo, el host no mostró una confirmación aparte de la autorización expresa del usuario.
