from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import Django
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.queue import Celery
from diagrams.onprem.network import Internet
from diagrams.generic.device import Mobile
from diagrams.onprem.monitoring import Grafana

graph_attr = {"fontsize": "20", "bgcolor": "white", "pad": "0.3"}

with Diagram("San Camilo en Linea - Vista de Despliegue", filename="despliegue", show=False,
             direction="LR", graph_attr=graph_attr, outformat="png"):
    
    # Usuarios y dispositivos
    usuarios = Users("Clientes y\nRepartidores")
    comerciante = Mobile("Comerciante PWA\n(Gama Baja / 3G)")
    
    with Cluster("Servidor VPS (Unico Nodo - Produccion)"):
        proxy = Nginx("Nginx Proxy\n(HTTPS / SSL)")
        
        with Cluster("Monolito Modular"):
            app = Django("Backend API\n(5 Modulos)")
            worker = Celery("Tareas Asincronas\n(Notificaciones)")
            
        cache = Redis("Redis\n(Cache + Cola)")
        db = PostgreSQL("PostgreSQL\n(Esquemas Aislados)")
        mon = Grafana("Grafana\n(Monitoreo)")

    # Servicios externos
    yape_api = Internet("Pasarela Yape API")
    whatsapp_api = Internet("WhatsApp Business API")

    # Flujo de conexiones
    usuarios >> proxy
    comerciante >> Edge(label="3G / PWA") >> proxy
    proxy >> app
    
    app >> db
    app >> Edge(label="Encola mensajes") >> cache >> worker
    
    worker >> Edge(label="Notificacion", style="dashed") >> whatsapp_api
    app >> Edge(label="Procesa Pago", style="dashed") >> yape_api
    app >> Edge(style="dotted") >> mon