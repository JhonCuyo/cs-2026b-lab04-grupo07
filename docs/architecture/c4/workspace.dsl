workspace "San Camilo en Línea" "Modelo C4 de la plataforma de comercio electrónico multipuesto del Mercado San Camilo" {

    !identifiers hierarchical

    model {
        # Personas (Actores de drivers.md)
        cliente = person "Cliente" "Ciudadano que busca productos en el mercado, realiza pedidos multipuesto y paga con Yape."
        comerciante = person "Comerciante" "Vendedor de puesto en el Mercado San Camilo que publica su catálogo y prepara pedidos desde gama baja/3G."
        repartidor = person "Repartidor" "Encargado de recoger los productos en los puestos y gestionar la entrega o despacho del pedido."

        # Sistema Principal, Contenedores (Nivel 2) y Componentes (Nivel 3)
        sancamilo = softwareSystem "San Camilo en Línea" "Permite consultar el catálogo por puesto, realizar pedidos unificados multipuesto, pagarlos y gestionar su preparación y entrega." {
            
            pwa = container "PWA San Camilo" "Aplicación web progresiva ligera optimizada para redes 3G y celulares de gama baja." "React + Service Worker" "Web Browser"
            
            api = container "Backend API" "Monolito modular que expone la lógica de negocio mediante una API REST." "Python / Django REST Framework" {
                catalogo = component "Módulo Catálogo" "Gestiona puestos del mercado, publicación de productos y reserva de stock." "Django app (catalogo)"
                pedidos = component "Módulo Pedidos" "Orquesta el carrito multipuesto, confirmación, ciclo de vida del pedido y asignación de entrega." "Django app (pedidos)"
                pagos = component "Módulo Pagos" "Procesa cobros desacoplados mediante el puerto PasarelaPago y su adaptador YapeAdapter." "Django app (pagos)"
                notificaciones = component "Módulo Notificaciones" "Gestiona el envío asíncrono de avisos a comerciantes mediante el puerto Notificador." "Django app (notificaciones)"
                reportes = component "Módulo Reportes" "Genera consultas y resúmenes de ventas por puesto en modo de solo lectura." "Django app (reportes)"
                compartido = component "Módulo Compartido" "Provee clases base de dominio, utilidades transversales y excepciones comunes." "Python package (compartido)"
            }
            
            worker = container "Worker de Tareas" "Procesa el envío asíncrono de notificaciones y reintentos sin bloquear las compras." "Celery"
            
            db = container "Base de Datos" "Almacena catálogo de puestos, pedidos multipuesto y pagos con esquemas aislados por módulo." "PostgreSQL 16" "Database"
            
            cola = container "Cola y Caché" "Broker de mensajería para tareas asíncronas y caché de lecturas del catálogo." "Redis" "Queue"
        }

        # Sistemas Externos
        yape = softwareSystem "Pasarela Yape API" "Procesa el cobro electrónico de los pedidos mediante billetera móvil." "Externo"
        whatsapp = softwareSystem "WhatsApp Business API" "Envía notificaciones de confirmación y detalle de pedidos a los comerciantes." "Externo"

        # Relaciones de Nivel 1 (Contexto)
        cliente -> sancamilo "Busca catálogo por puesto, realiza pedidos multipuesto y paga"
        comerciante -> sancamilo "Publica catálogo en pocos pasos, consulta ventas y actualiza preparación de pedidos"
        repartidor -> sancamilo "Consulta pedidos asignados y registra el estado de recojo/delivery"
        sancamilo -> yape "Solicita cobros de pedidos" "HTTPS/JSON"
        sancamilo -> whatsapp "Envía notificaciones de pedidos confirmados" "HTTPS/JSON"

        # Relaciones de Nivel 2 (Contenedores)
        cliente -> sancamilo.pwa "Navega el catálogo y realiza pedidos desde su navegador" "HTTPS"
        comerciante -> sancamilo.pwa "Gestiona productos y pedidos en red 3G" "HTTPS"
        repartidor -> sancamilo.pwa "Consulta hojas de recojo y actualiza entregas" "HTTPS"

        sancamilo.pwa -> sancamilo.api "Realiza peticiones a la API" "HTTPS/JSON (REST)"
        sancamilo.api -> sancamilo.db "Lee y escribe registros en esquemas aislados" "SQL/TCP"
        sancamilo.api -> sancamilo.cola "Encola eventos de notificación y consulta caché de catálogo" "Redis protocol"
        sancamilo.worker -> sancamilo.cola "Consume tareas de notificación encoladas" "Redis protocol"
        
        sancamilo.api -> yape "Solicita cobro electrónico del pedido" "HTTPS/JSON"
        sancamilo.worker -> whatsapp "Envía mensaje de confirmación al comerciante" "HTTPS/JSON"

        # Relaciones de Nivel 3 (Componentes de Backend API)
        sancamilo.pwa -> sancamilo.api.catalogo "Consulta puestos y publica productos" "HTTPS/JSON (REST)"
        sancamilo.pwa -> sancamilo.api.pedidos "Crea, confirma y actualiza pedidos multipuesto" "HTTPS/JSON (REST)"
        sancamilo.pwa -> sancamilo.api.reportes "Consulta reportes de ventas por puesto" "HTTPS/JSON (REST)"

        sancamilo.api.pedidos -> sancamilo.api.catalogo "Valida productos por puesto y reserva stock" "Llamada interna Python"
        sancamilo.api.pedidos -> sancamilo.api.pagos "Solicita cobro mediante puerto PasarelaPago" "Llamada interna Python"
        sancamilo.api.pedidos -> sancamilo.api.notificaciones "Solicita aviso de nuevo pedido mediante puerto Notificador" "Llamada interna Python"
        sancamilo.api.reportes -> sancamilo.api.pedidos "Consulta pedidos históricos (solo lectura)" "Llamada interna Python"

        sancamilo.api.catalogo -> sancamilo.api.compartido "Usa abstracciones base y utilidades" "Importación Python"
        sancamilo.api.pedidos -> sancamilo.api.compartido "Usa abstracciones base y utilidades" "Importación Python"
        sancamilo.api.pagos -> sancamilo.api.compartido "Usa abstracciones base y utilidades" "Importación Python"
        sancamilo.api.notificaciones -> sancamilo.api.compartido "Usa abstracciones base y utilidades" "Importación Python"
        sancamilo.api.reportes -> sancamilo.api.compartido "Usa abstracciones base y utilidades" "Importación Python"

        sancamilo.api.catalogo -> sancamilo.db "Lee y escribe productos y puestos" "SQL/TCP"
        sancamilo.api.catalogo -> sancamilo.cola "Lee y actualiza caché de catálogo" "Redis protocol"
        sancamilo.api.pedidos -> sancamilo.db "Lee y escribe pedidos multipuesto" "SQL/TCP"
        sancamilo.api.pagos -> sancamilo.db "Registra transacciones de pago" "SQL/TCP"
        sancamilo.api.pagos -> yape "Ejecuta cobro electrónico mediante YapeAdapter" "HTTPS/JSON"
        sancamilo.api.notificaciones -> sancamilo.cola "Encola tarea asíncrona de notificación" "Redis protocol"

        # Entorno de Despliegue (E5 - Coherente con R-03, R-04 y despliegue.py)
        produccion = deploymentEnvironment "Producción" {
            
            deploymentNode "Dispositivo del Usuario (Cliente / Comerciante / Repartidor)" "Smartphones Android de gama baja (conectividad 3G) o navegador en PC." "Android / Navegador Web (Chrome Mobile)" {
                containerInstance sancamilo.pwa
            }

            deploymentNode "Servidor VPS en la Nube (Único Nodo - R-03)" "Servidor virtual económico con proxy inverso Nginx (HTTPS/SSL) y monitoreo básico." "Ubuntu 24.04 LTS (2 vCPU, 4 GB RAM, 80 GB SSD)" {
                
                deploymentNode "Docker Compose" "Orquestador local de contenedores en un solo nodo para el MVP." "Docker Engine 27 + Nginx Reverse Proxy" {
                    containerInstance sancamilo.api
                    containerInstance sancamilo.worker
                    containerInstance sancamilo.db
                    containerInstance sancamilo.cola
                }
            }
        }
    }

    views {
        systemContext sancamilo "Contexto" "Nivel 1: Diagrama de Contexto de San Camilo en Línea y su entorno." {
            include *
            autolayout lr
        }

        container sancamilo "Contenedores" "Nivel 2: Contenedores que conforman San Camilo en Línea." {
            include *
            autolayout lr
        }

        component sancamilo.api "Componentes" "Nivel 3: Componentes internos del Monolito Modular (Backend API)." {
            include *
            autolayout lr
        }

        dynamic sancamilo.api "ConfirmarYPagar" "Vista Dinámica: Confirmar pedido multipuesto y pagar con Yape." {
            sancamilo.pwa -> sancamilo.api.pedidos "POST /pedidos/{id}/pago (confirmarYPagar)"
            sancamilo.api.pedidos -> sancamilo.db "Busca el pedido multipuesto por ID"
            sancamilo.api.pedidos -> sancamilo.api.catalogo "Reserva stock por cada línea del pedido"
            sancamilo.api.pedidos -> sancamilo.api.pagos "Solicita cobro del total calculado (puerto PasarelaPago)"
            sancamilo.api.pagos -> yape "Ejecuta cobro electrónico (cobrar total y celular)"
            sancamilo.api.pagos -> sancamilo.db "Registra transacción de pago aprobada"
            sancamilo.api.pedidos -> sancamilo.db "Actualiza estado del pedido a PAGADO"
            sancamilo.api.pedidos -> sancamilo.api.notificaciones "Solicita notificar nuevo pedido (puerto Notificador)"
            sancamilo.api.notificaciones -> sancamilo.cola "Encola mensaje asíncrono para WhatsApp por comerciante"
            autolayout lr
        }

        deployment sancamilo "Producción" "Despliegue" "Vista de Despliegue en el entorno de Producción (MVP en VPS único)." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Queue" {
                shape pipe
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}