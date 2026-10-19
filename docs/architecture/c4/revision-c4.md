# Revisión de Calidad del Modelo C4 — San Camilo en Línea

## 1. Aplicación de la Lista de Revisión Oficial C4 (`c4model.com/diagrams/checklist`)

| Grupo | Pregunta de Revisión Oficial | Contexto (N1) | Contenedores (N2) | Componentes (N3) | Dinámico | Despliegue | Evidencia en los diagramas generados |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **General** | ¿Tiene título que identifique el tipo de diagrama y su alcance? | Sí | Sí | Sí | Sí | Sí | Encabezados automáticos de C4-PlantUML: `System Context View: San Camilo en Línea`, `Container View: San Camilo en Línea`, `Component View: San Camilo en Línea - Backend API`, `Dynamic View` y `Deployment View`. |
| **General** | ¿Tiene leyenda (`SHOW_LEGEND`) que explique colores, formas y bordes? | Sí | Sí | Sí | Sí | Sí | Todas las vistas exportadas e imágenes PNG incluyen el bloque `Legend` en la esquina inferior derecha. |
| **Elementos** | ¿Cada elemento tiene nombre, tipo (`Person`, `System`, `Container`, `Component`, `Node`) y descripción? | Sí | Sí | Sí | Sí | Sí | Cada caja muestra su nombre en negrita, su estereotipo entre corchetes y un resumen de su responsabilidad. |
| **Elementos** | ¿Los contenedores, componentes y nodos indican su tecnología concreta (y el Nivel 1 la omite)? | Sí | Sí | Sí | Sí | Sí | Nivel 1 no expone tecnologías internas; Nivel 2 especifica `React + Service Worker`, `Python / Django REST Framework`, `Celery`, `PostgreSQL 16` y `Redis`; Nivel 3 indica `Django app`; Despliegue detalla `Ubuntu 24.04 LTS (2 vCPU, 4 GB RAM)`. |
| **Elementos** | ¿Se entienden los acrónimos, formas (`cylinder`, `pipe`, `WebBrowser`) y colores (`Externo` en gris)? | Sí | Sí | Sí | Sí | Sí | `PostgreSQL 16` usa forma cilíndrica (`Database`), `Redis` usa forma de cola (`Queue`), `PWA` usa forma de navegador (`WebBrowser`) y `Yape`/`WhatsApp` se distinguen en gris (`#999999`). |
| **Relaciones** | ¿Cada flecha tiene una etiqueta con verbo que describe su intención (no solo "usa") y coincide con su dirección? | Sí | Sí | Sí | Sí | Sí | Etiquetas específicas como *"Solicita cobro electrónico del pedido"*, *"Reserva stock por cada línea del pedido"* y *"Encola tarea asíncrona de notificación"*. |
| **Relaciones** | ¿Se indica el protocolo o tecnología de comunicación en las interacciones técnicas? | Sí | Sí | Sí | Sí | Sí | Se detallan `[HTTPS]`, `[HTTPS/JSON (REST)]`, `[SQL/TCP]`, `[Redis protocol]` y `[Llamada interna Python]`. |

---

## 2. Auditoría con IA (Prompt IA 2) y Verificación del Equipo

Resultado de someter los archivos `.puml` exportados al Prompt IA 2 (Auditor C4) y evaluación crítica por parte del equipo:

| Vista | Hallazgo reportado por la IA | Clasificación | Verificación y decisión del equipo |
| :--- | :--- | :---: | :--- |
| **Contexto (Nivel 1)** | *"Falta indicar el protocolo `[HTTPS]` en las tres relaciones entre las Personas (`Cliente`, `Comerciante`, `Repartidor`) y el sistema `San Camilo en Línea`."* | **Falso positivo 1** | **Descartado:** En el Nivel 1 (Contexto) el público incluye personas no técnicas (como la junta de comerciantes del mercado); las interacciones de negocio de los actores humanos con el sistema no exigen especificar protocolos de red (estos recién se detallan en el Nivel 2 hacia la PWA). |
| **Componentes (Nivel 3)** | *"Las relaciones entre `Módulo Pedidos` y los módulos `Catálogo`, `Pagos` y `Notificaciones` no usan un protocolo de red como HTTP o gRPC."* | **Falso positivo 2** | **Descartado:** Según el `ADR-001`, el sistema es un **Monolito Modular** desplegado en un solo proceso Django, no microservicios. Por tanto, la comunicación entre componentes internos ocurre en memoria (`Llamada interna Python`) a través de interfaces públicas. |
| **Contenedores (Nivel 2)** | *"La relación de `Backend API` hacia `Cola y Caché (Redis)` dice 'Encola eventos de notificación y consulta caché de catálogo', combinando dos responsabilidades en una sola flecha."* | **Observación válida aceptada** | **Se mantiene documentado:** En Structurizr DSL las relaciones entre dos elementos sobre un mismo protocolo (`Redis protocol`) se consolidan para evitar saturar visualmente el diagrama, desglosándose luego en la vista de Nivel 3 (`Módulo Catálogo` lee caché y `Módulo Notificaciones` encola tareas). |
| **Despliegue** | *"En `despliegue.py` del Lab 04 aparecía Nginx como un nodo separado, mientras que en el modelo C4 no aparece como un contenedor del sistema."* | **Correcto (Cumple regla C4)** | **Verificado:** Nginx actúa como proxy inverso de infraestructura en el VPS único; por ello se documenta en la tecnología/descripción del nodo de despliegue (`Docker Engine 27 + Nginx Reverse Proxy`) sin contaminar la lista de contenedores de aplicación del Nivel 2. |