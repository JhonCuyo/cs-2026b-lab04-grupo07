"""Ejecuta el agente ReAct con mapa_repo y memoria de notas sobre ISSUE-03."""

import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import ModeloGrabado
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica


def main():
    h = Herramientas(RAIZ)
    modelo = ModeloGrabado(RAIZ / "agentes" / "trayectorias" / "issue03_ejecutor.json")
    objetivo = (
        "Resuelve issues/ISSUE-03.md usando mapa_repo() y la memoria de notas (anotar/leer_notas). "
        f"Herramientas: {h.catalogo()}"
    )
    agente = Agente(
        nombre="ejecutor_issue03",
        modelo=modelo,
        herramientas=h,
        politica=Politica(max_pasos=12),
        objetivo=objetivo,
        traza_archivo=RAIZ / "agentes" / "trazas" / "issue03_ejecutor.jsonl",
    )
    print(agente.ejecutar())


if __name__ == "__main__":
    main()
