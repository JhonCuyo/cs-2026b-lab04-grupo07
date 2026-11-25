"""Ejecuta el agente ReAct del Lab 10 conectado al servidor MCP sancamilo a través del espía stdio."""

import argparse
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from agentes.agente.modelos import ModeloGrabado, ModeloInteractivo
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica, solicitar_aprobacion_consola
from agentes.mcp.agente.herramientas_mcp import HerramientasMCP


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactivo", action="store_true")
    parser.add_argument("--sin-confirmacion", action="store_true")
    args = parser.parse_args()

    traza_rpc = RAIZ / "agentes" / "mcp" / "trazas" / "mcp_trafico.jsonl"
    if traza_rpc.exists():
        traza_rpc.unlink()

    espia = str(RAIZ / "agentes" / "mcp" / "cliente" / "espia.py")
    servidor = str(RAIZ / "agentes" / "mcp" / "servidor_mcp" / "sancamilo_mcp.py")

    with HerramientasMCP(sys.executable, [espia, str(traza_rpc), sys.executable, servidor]) as h_mcp:
        escritura = h_mcp.herramientas_de_escritura()
        politica = Politica(
            herramientas_permitidas=set(h_mcp.catalogo().keys()),
            requieren_aprobacion=escritura,
            aprobar_edicion=None if args.sin_confirmacion else solicitar_aprobacion_consola,
            max_pasos=10,
        )
        ruta_tray = RAIZ / "agentes" / "mcp" / "trayectorias" / "consulta_sancamilo.json"
        modelo = ModeloInteractivo(ruta_tray) if args.interactivo else ModeloGrabado(ruta_tray)
        agente = Agente(
            nombre="agente_sancamilo_mcp",
            modelo=modelo,
            herramientas=h_mcp,
            politica=politica,
            objetivo=f"Verifica disponibilidad de rocoto y pedidos pagados del puesto A-01, y registra un borrador para Cliente-05. Catálogo: {h_mcp.catalogo()}",
            traza_archivo=RAIZ / "agentes" / "mcp" / "trazas" / "agente_mcp.jsonl",
        )
        print(agente.ejecutar())


if __name__ == "__main__":
    main()
