workspace "San Camilo en Línea" "Modelo C4 de la plataforma de comercio electrónico multipuesto del Mercado San Camilo" {

    !identifiers hierarchical

    model {
        # Personas (Actores de drivers.md)
        cliente = person "Cliente" "Ciudadano que busca productos en el mercado, realiza pedidos multipuesto y paga con Yape."
        comerciante = person "Comerciante" "Vendedor de puesto en el Mercado San Camilo que publica su catálogo y prepara pedidos desde gama baja/3G."
        repartidor = person "Repartidor" "Encargado de recoger los productos en los puestos y gestionar la entrega o despacho del pedido."

        # Sistema Principal
        sancamilo = softwareSystem "San Camilo en Línea" "Permite consultar el catálogo por puesto, realizar pedidos unificados multipuesto, pagarlos y gestionar su preparación y entrega."

        # Sistemas Externos
        yape = softwareSystem "Pasarela Yape API" "Procesa el cobro electrónico de los pedidos mediante billetera móvil." "Externo"
        whatsapp = softwareSystem "WhatsApp Business API" "Envía notificaciones de confirmación y detalle de pedidos a los comerciantes." "Externo"

        # Relaciones de Nivel 1 (Contexto)
        cliente -> sancamilo "Busca catálogo por puesto, realiza pedidos multipuesto y paga"
        comerciante -> sancamilo "Publica catálogo en pocos pasos, consulta ventas y actualiza preparación de pedidos"
        repartidor -> sancamilo "Consulta pedidos asignados y registra el estado de recojo/delivery"

        sancamilo -> yape "Solicita cobros de pedidos" "HTTPS/JSON"
        sancamilo -> whatsapp "Envía notificaciones de pedidos confirmados" "HTTPS/JSON"
    }

    views {
        systemContext sancamilo "Contexto" "Nivel 1: Diagrama de Contexto de San Camilo en Línea y su entorno." {
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
        }
    }
}