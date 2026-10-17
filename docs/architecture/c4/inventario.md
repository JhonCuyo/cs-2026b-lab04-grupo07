# Inventario de Elementos del Modelo C4 — San Camilo en Línea

Tabla de trazabilidad de los elementos arquitectónicos extraídos de los artefactos de los Laboratorios 04 y 05:

| Elemento | Tipo C4 | Origen (Artefacto Lab 04 / Lab 05) |
| :--- | :--- | :--- |
| **Cliente (Comprador)**, **Comerciante**, **Repartidor** | Persona | `docs/architecture/drivers.md` (RF-01 al RF-05, QA-01, QA-02) y `secuencia-confirmar-pagar.puml` |
| **San Camilo en Línea** | Sistema de software | Caso asignado N.° 7 (`drivers.md` y `ADR-001`) |
| **Pasarela Yape API**, **WhatsApp Business API** | Sistema externo | `docs/architecture/drivers.md` (RF-03, RF-04), `ADR-001` y `despliegue.py` |
| **PWA San Camilo**, **Backend API (Monolito Modular)**, **Worker de Tareas (Celery)**, **Base de Datos (PostgreSQL)**, **Cola y Caché (Redis)** | Contenedor | `docs/architecture/adr/001-estilo-arquitectonico.md` y `despliegue.py` (Lab 04) |
| **Módulo Catálogo**, **Módulo Pedidos**, **Módulo Pagos**, **Módulo Notificaciones**, **Módulo Reportes**, **Módulo Compartido** | Componente (de la API) | `docs/design/paquetes.puml` (Lab 05) |
| **Flujo "Confirmar pedido multipuesto y pagar con Yape"** | Vista dinámica | `docs/design/secuencia-confirmar-pagar.puml` (Lab 05) |
| **PedidoMultipuesto, PedidoController, ServicioPedidos, RepositorioPedidos, PasarelaPago (YapeAdapter), Notificador** | Código (Nivel 4 - no se redibuja en C4) | `docs/design/clases.puml` y `secuencia-confirmar-pagar.puml` (Lab 05) |