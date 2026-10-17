workspace "San Camilo en Línea" "Modelo C4 de la plataforma de comercio electrónico multipuesto del Mercado San Camilo" {

    !identifiers hierarchical

    model {
        # Personas
        cliente = person "Cliente" "Ciudadano que busca productos en el mercado, realiza pedidos multipuesto y paga con Yape."
        comerciante = person "Comerciante" "Vendedor de puesto en el Mercado San Camilo que publica su catálogo y prepara pedidos desde gama baja/3G."
        repartidor = person "Repartidor" "Encargado de recoger los productos en los puestos y gestionar la entrega o despacho del pedido."

        # Sistema Principal y Contenedores (Nivel 2)
        sancamilo = softwareSystem "San Camilo en Línea" "Permite consultar el catálogo por puesto, realizar pedidos unificados multipuesto, pagarlos y gestionar su preparación y entrega." {
            
            pwa = container "PWA San Camilo" "Aplicación web progresiva ligera optimizada para redes 3G y celulares de gama baja." "React + Service Worker" "Web Browser"
            
            api = container "Backend API" "Monolito modular que expone la lógica de negocio mediante una API REST." "Python / Django REST Framework"
            
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