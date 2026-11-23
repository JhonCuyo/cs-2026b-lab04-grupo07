# Catálogo del Servidor MCP — San Camilo en Línea (Grupo 07)

## 1. Tabla de Capacidades y Primitivas (Especificación MCP 2026-07-28)

| Capacidad | Primitiva | Nombre / URI | ¿Escribe? | Justificación |
| :--- | :--- | :--- | :---: | :--- |
| Buscar productos visibles del catálogo | Herramienta (`tool`) | `buscar_producto` | No (solo lectura) | Consulta filtrada por término y/o puesto reutilizando `listar_productos_visibles()` (`src/sancamilo/catalogo/productos.py`); tope de 20 resultados para no saturar el contexto. |
| Resumen de pedidos y montos por puesto | Herramienta (`tool`) | `pedidos_por_puesto` | No (solo lectura) | Cálculo estructurado (`TypedDict`) que reutiliza `calcular_total_soles()` y `calcular_comision_pedido()` (`src/sancamilo/pedidos/`). |
| Verificar estado de la suite de pruebas | Herramienta (`tool`) | `ejecutar_pruebas` | No (solo lectura) | Verificación rápida con `pytest -q` sobre `tests/` sin modificar archivos. |
| Registrar un pedido en borrador | Herramienta (`tool`) | `registrar_pedido_borrador` | **Sí, solo crea** | Única herramienta de escritura: crea un archivo nuevo `agentes/mcp/borradores/PEDIDO-NN.json`; nunca edita ni borra archivos existentes. |
| Catálogo de puestos del mercado | Recurso (`resource`) | `sancamilo://catalogo/puestos` | No | Contexto estable controlado por el host (lista de puestos y rubros del Mercado San Camilo). |
| Estados del pedido y reglas de comisión | Recurso (`resource`) | `sancamilo://pedidos/estados` | No | Contexto estable del dominio para evitar que el modelo asuma estados inválidos. |
| Decisiones de arquitectura (ADR) | Recurso plantilla | `sancamilo://adr/{numero}` | No | Permite al host leer cualquier ADR (`001` a `011`) validando estrictamente 3 dígitos (`^\d{3}$`) para bloquear *path traversal*. |
| Redactar oferta diaria para comerciantes | Prompt (`prompt`) | `oferta_del_dia` | No | Plantilla controlada por el usuario para generar avisos claros de oferta por puesto. |
| Normalizar producto del catálogo (Lab 09) | Prompt (`prompt`) | `normalizar_catalogo_producto` | No | Reutiliza la plantilla `prompts/sancamilo_normalizar/v3.txt` del Lab 09 con delimitadores `<producto>` contra inyección. |

## 2. Descripciones de Herramientas (redactadas antes de programar)

- **`buscar_producto(termino: str = "", puesto: str = "") -> list[dict]`**
  - *Qué hace:* Lista productos activos y con `stock > 0` del catálogo de San Camilo en Línea.
  - *Parámetros:* `termino` (texto opcional para filtrar por nombre, máx. 60 caracteres); `puesto` (código opcional de puesto, ej. `"A-01"`, máx. 20 caracteres).
  - *Devuelve:* Lista JSON de hasta 20 objetos `{id, nombre, puesto, precio, stock}`.
- **`pedidos_por_puesto(puesto: str, estado: str = "") -> ResumenPuesto`**
  - *Qué hace:* Consulta pedidos ficticios de un puesto y calcula el total en soles (`Decimal` `ROUND_HALF_UP`) y la comisión aplicable.
  - *Parámetros:* `puesto` (obligatorio, ej. `"A-01"`, `"A-02"`, `"B-05"`); `estado` (opcional: `BORRADOR`, `CONFIRMADO`, `PAGADO`, `EN_PREPARACION`, `ENTREGADO` o `CANCELADO`).
  - *Devuelve:* Salida estructurada (`outputSchema` / `structuredContent`) con `{puesto, estado_filtro, cantidad_pedidos, total_soles, comision_fija, pedidos}`.
- **`ejecutar_pruebas() -> str`**
  - *Qué hace:* Ejecuta `pytest -q` sobre `tests/` y devuelve la línea de resumen final. No recibe parámetros ni modifica archivos.
- **`registrar_pedido_borrador(cliente: str, puesto: str, producto: str, cantidad: int) -> str`**
  - *Qué hace:* Registra un borrador de pedido creando un archivo JSON secuencial nuevo (`PEDIDO-NN.json`) en `agentes/mcp/borradores/`.
  - *Parámetros:* `cliente` (nombre anonimizado, 3–60 caracteres), `puesto` (código de puesto existente, ej. `"A-01"`), `producto` (nombre de producto, 2–80 caracteres), `cantidad` (entero entre 1 y 50).
  - *Devuelve:* Ruta relativa del archivo borrador creado.

## 3. Justificación de Seguridad de la Herramienta de Escritura

`registrar_pedido_borrador` no puede causar daño irreversible porque:
1. **Solo crea archivos nuevos** con numeración secuencial automática (`PEDIDO-01.json`, `PEDIDO-02.json`, ...); nunca sobrescribe ni elimina archivos existentes ni toca `src/` o `tests/`.
2. **Está aislada en `agentes/mcp/borradores/`** (no altera base de datos real, no dispara cobros Yape ni mensajes de WhatsApp).
3. **Declara anotaciones explícitas** (`read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False`), de modo que tanto el host real como la política del agente del Lab 10 exigen **aprobación humana** antes de ejecutarla.
