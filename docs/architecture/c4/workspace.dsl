workspace "San Camilo en Línea 2.0" "Modelo C4 multimercado (San Camilo, Altiplano y Río Seco) refinado con ADD 3.0" {

    !identifiers hierarchical

    model {
        # Personas
        cliente = person "Cliente" "Ciudadano que compra productos de puestos de San Camilo, Altiplano o Río Seco y paga con Yape/Plin."
        comerciante = person "Comerciante" "Vendedor de puesto en San Camilo, Altiplano o Río Seco con smartphone de gama baja y red 3G."
        repartidor = person "Repartidor" "Encargado de recoger los productos en los puestos del mercado correspondiente y entregarlos."

        # Sistema Principal (Nivel 2 y Nivel 3 con trazabilidad a escenarios QA-01..QA-07)
        sancamilo = softwareSystem "San Camilo en Línea 2.0 (Multimercado)" "Plataforma de comercio electrónico multipuesto para los mercados San Camilo, Altiplano y Río Seco." {
            
            pwa = container "PWA Offline-first" "Guarda cambios de catálogo en IndexedDB sin señal 3G y los sincroniza al recuperar red [QA-05]." "React + Service Worker + IndexedDB" "Web Browser"
            
            api = container "Backend API (Monolito Modular)" "Valida claim 'mercado_id' en cada JWT [QA-01], aplica reglas por mercado desde BD [QA-02] y protege pagos con Circuit Breaker [QA-04, QA-06]." "Python / Django REST + JWT" {
                catalogo = component "Módulo Catálogo" "Consulta catálogo con caché Redis e índice compuesto [QA-03] y sincroniza lotes offline [QA-05]." "Django app (catalogo)"
                pedidos = component "Módulo Pedidos" "Orquesta pedidos multipuesto aplicando tarifas parametrizadas por mercado [QA-02] y máquina de estados State." "Django app (pedidos)"
                pagos = component "Módulo Pagos" "Cobra mediante puerto PasarelaPago con Reintentos, Circuit Breaker y registro en tabla Outbox [QA-04, QA-06]." "Django app (pagos)"
                notificaciones = component "Módulo Notificaciones" "Publica eventos Observer y encola avisos de WhatsApp por comerciante [QA-04]." "Django app (notificaciones)"
                reportes = component "Módulo Reportes" "Genera reportes aislados por mercado mediante políticas RLS [QA-01]." "Django app (reportes)"
                compartido = component "Módulo Compartido" "Middleware JWT de tenant (mercado_id), configuración multimercado y utilidades base [QA-01, QA-02]." "Python package (compartido)"
            }
            
            worker = container "Worker de Tareas" "Procesa la tabla outbox_pagos de cobros pendientes y despacha notificaciones de WhatsApp [QA-04]." "Celery"
            
            db = container "Base de Datos" "Almacena tablas con índices compuestos [QA-03], Row-Level Security (RLS) por mercado [QA-01], configuración de mercados [QA-02] y tabla outbox_pagos [QA-04]." "PostgreSQL 16 + RLS" "Database"
            
            cola = container "Caché y Cola" "Caché de catálogo particionada por mercado con TTL de 30 s [QA-03] y broker de tareas de notificación." "Redis" "Queue"
        }

        # Sistemas Externos
        yape = softwareSystem "Proveedor de Pagos (Yape / Plin)" "Procesa cobros electrónicos mediante billetera móvil." "Externo"
        whatsapp = softwareSystem "WhatsApp Business API" "Envía notificaciones de pedidos confirmados a cada comerciante." "Externo"

        # Relaciones de Nivel 1 (Contexto)
        cliente -> sancamilo "Busca catálogo por mercado/puesto, realiza pedidos multipuesto y paga"
        comerciante -> sancamilo "Publica su catálogo (incluso sin señal 3G) y atiende pedidos de su puesto"
        repartidor -> sancamilo "Consulta hojas de recojo por mercado y actualiza entregas"
        sancamilo -> yape "Solicita cobros con reintentos y circuit breaker [QA-04]" "HTTPS/JSON"
        sancamilo -> whatsapp "Envía notificaciones a comerciantes" "HTTPS/JSON"

        # Relaciones de Nivel 2 (Contenedores)
        cliente -> sancamilo.pwa "Compra y paga [QA-07]" "HTTPS (TLS 1.3)"
        comerciante -> sancamilo.pwa "Registra stock sin señal y sincroniza [QA-05]" "HTTPS (TLS 1.3)"
        repartidor -> sancamilo.pwa "Gestiona entregas [QA-07]" "HTTPS (TLS 1.3)"

        sancamilo.pwa -> sancamilo.api "Sincroniza y consulta con token JWT (claim mercado_id) [QA-01, QA-05]" "HTTPS/JSON"
        sancamilo.api -> sancamilo.cola "Lee catálogo en caché (TTL 30 s) y encola avisos [QA-03]" "Redis protocol"
        sancamilo.api -> sancamilo.db "Lee y escribe con RLS por mercado, índices y tabla outbox [QA-01, QA-02, QA-03, QA-04]" "SQL/TCP"
        sancamilo.worker -> sancamilo.db "Lee y actualiza tabla outbox_pagos pendientes [QA-04]" "SQL/TCP"
        sancamilo.worker -> sancamilo.cola "Consume tareas de notificación" "Redis protocol"
        
        sancamilo.api -> yape "Cobra con reintentos y circuit breaker [QA-04]" "HTTPS/JSON"
        sancamilo.worker -> yape "Reintenta pagos diferidos de la tabla outbox [QA-04]" "HTTPS/JSON"
        sancamilo.worker -> whatsapp "Envía mensaje de confirmación al comerciante" "HTTPS/JSON"

        # Relaciones de Nivel 3 (Componentes)
        sancamilo.pwa -> sancamilo.api.catalogo "Consulta puestos y sincroniza productos [QA-03, QA-05]" "HTTPS/JSON"
        sancamilo.pwa -> sancamilo.api.pedidos "Confirma y paga pedidos multipuesto [QA-02, QA-04]" "HTTPS/JSON"
        sancamilo.pwa -> sancamilo.api.reportes "Consulta ventas de su mercado [QA-01]" "HTTPS/JSON"

        sancamilo.api.pedidos -> sancamilo.api.catalogo "Reserva stock por línea" "Llamada interna Python"
        sancamilo.api.pedidos -> sancamilo.api.pagos "Solicita cobro mediante puerto PasarelaPago [QA-04, QA-06]" "Llamada interna Python"
        sancamilo.api.pedidos -> sancamilo.api.notificaciones "Publica evento pedido_pagado" "Llamada interna Python"
        sancamilo.api.reportes -> sancamilo.api.pedidos "Consulta pedidos históricos (solo lectura)" "Llamada interna Python"

        sancamilo.api.catalogo -> sancamilo.api.compartido "Verifica tenant mercado_id [QA-01]" "Importación Python"
        sancamilo.api.pedidos -> sancamilo.api.compartido "Obtiene tarifas de ConfiguracionMercado [QA-02]" "Importación Python"
        sancamilo.api.pagos -> sancamilo.api.compartido "Usa abstracciones base" "Importación Python"
        sancamilo.api.notificaciones -> sancamilo.api.compartido "Usa abstracciones base" "Importación Python"
        sancamilo.api.reportes -> sancamilo.api.compartido "Verifica tenant mercado_id [QA-01]" "Importación Python"

        sancamilo.api.catalogo -> sancamilo.cola "Lee caché de catálogo (TTL 30 s) [QA-03]" "Redis protocol"
        sancamilo.api.catalogo -> sancamilo.db "Consulta productos con índice compuesto y RLS [QA-01, QA-03]" "SQL/TCP"
        sancamilo.api.pedidos -> sancamilo.db "Persiste pedido multipuesto con RLS [QA-01]" "SQL/TCP"
        sancamilo.api.pagos -> sancamilo.db "Registra pago o difiere en tabla outbox_pagos [QA-04]" "SQL/TCP"
        sancamilo.api.pagos -> yape "Ejecuta cobro protegido por ConCircuitBreaker [QA-04]" "HTTPS/JSON"
        sancamilo.api.notificaciones -> sancamilo.cola "Encola aviso de WhatsApp" "Redis protocol"

        # Entorno de Despliegue
        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Smartphone del Usuario (3G / Gama Baja)" "Android con navegador Chrome Mobile e IndexedDB." "Android / Web Browser" {
                containerInstance sancamilo.pwa
            }
            deploymentNode "Servidor VPS en la Nube (Único Nodo - R-03)" "Disco cifrado y Nginx con TLS 1.3 [QA-07]." "Ubuntu 24.04 LTS (2 vCPU, 4 GB RAM)" {
                deploymentNode "Docker Compose" "Orquestador local del MVP multimercado." "Docker Engine 27 + Nginx" {
                    containerInstance sancamilo.api
                    containerInstance sancamilo.worker
                    containerInstance sancamilo.db
                    containerInstance sancamilo.cola
                }
            }
        }
    }

    views {
        systemContext sancamilo "Contexto" "Nivel 1: San Camilo en Línea 2.0 (San Camilo, Altiplano y Río Seco)." {
            include *
            autolayout lr
        }
        container sancamilo "Contenedores" "Nivel 2: Contenedores después de tres iteraciones de ADD 3.0." {
            include *
            autolayout lr
        }
        component sancamilo.api "Componentes" "Nivel 3: Componentes del Monolito Modular con tácticas ADD." {
            include *
            autolayout lr
        }
        dynamic sancamilo.api "ConfirmarYPagar" "Vista Dinámica: Confirmar pedido multipuesto con Circuit Breaker y Outbox." {
            sancamilo.pwa -> sancamilo.api.pedidos "POST /pedidos/{id}/pago (con JWT mercado_id)"
            sancamilo.api.pedidos -> sancamilo.api.compartido "Lee tarifa parametrizada del mercado [QA-02]"
            sancamilo.api.pedidos -> sancamilo.api.catalogo "Reserva stock validado"
            sancamilo.api.pedidos -> sancamilo.api.pagos "Solicita cobro (PasarelaPago + ConCircuitBreaker)"
            sancamilo.api.pagos -> yape "Intenta cobro o abre circuito [QA-04]"
            sancamilo.api.pagos -> sancamilo.db "Registra pago o inserta en outbox_pagos [QA-04]"
            sancamilo.api.pedidos -> sancamilo.api.notificaciones "Publica pedido_pagado"
            sancamilo.api.notificaciones -> sancamilo.cola "Encola aviso WhatsApp"
            autolayout lr
        }
        deployment sancamilo produccion "Despliegue" "Despliegue en Producción (VPS único con TLS 1.3)." {
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