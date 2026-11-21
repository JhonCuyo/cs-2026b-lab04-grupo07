"""Ejecuta el agente ReAct único sobre el ISSUE-01 (modo grabado o interactivo)."""

import argparse
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import ModeloGrabado, ModeloInteractivo
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactivo", action="store_true", help="Usar ModeloInteractivo en lugar de trayectoria grabada")
    args = parser.parse_args()

    h = Herramientas(RAIZ)
    ruta_tray = RAIZ / "agentes" / "trayectorias" / "issue01_ejecutor.json"
    modelo = ModeloInteractivo(ruta_tray) if args.interactivo else ModeloGrabado(ruta_tray)
    objetivo = (
        "Resuelve issues/ISSUE-01.md sin modificar archivos dentro de tests/. "
        f"Herramientas disponibles: {h.catalogo()}"
    )
    agente = Agente(
        nombre="ejecutor_issue01",
        modelo=modelo,
        herramientas=h,
        politica=Politica(max_pasos=12),
        objetivo=objetivo,
        traza_archivo=RAIZ / "agentes" / "trazas" / "issue01_ejecutor.jsonl",
    )
    print(agente.ejecutar())


if __name__ == "__main__":
    main()
