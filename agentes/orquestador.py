"""Orquestador del sistema agéntico para ISSUE-02: modo único vs. actor-crítico."""

import argparse
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import ModeloGrabado
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica, solicitar_aprobacion_consola
from agentes.agente.traza import cargar_eventos, generar_mermaid, resumir_metricas

MAX_RONDAS = 2


def ejecutar_unico(h: Herramientas, aprobar_edicion=None) -> list[pathlib.Path]:
    traza = RAIZ / "agentes" / "trazas" / "issue02_unico.jsonl"
    agente = Agente(
        nombre="unico_issue02",
        modelo=ModeloGrabado(RAIZ / "agentes" / "trayectorias" / "issue02_unico.json"),
        herramientas=h,
        politica=Politica(max_pasos=12, aprobar_edicion=aprobar_edicion),
        objetivo=f"Resuelve issues/ISSUE-02.md. Herramientas: {h.catalogo()}",
        traza_archivo=traza,
    )
    print("--- AGENTE ÚNICO ---")
    print(agente.ejecutar())
    return [traza]


def ejecutar_actor_critico(h: Herramientas, aprobar_edicion=None) -> list[pathlib.Path]:
    trazas: list[pathlib.Path] = []
    traza_plan = RAIZ / "agentes" / "trazas" / "issue02_planificador.jsonl"
    planificador = Agente(
        nombre="planificador",
        modelo=ModeloGrabado(RAIZ / "agentes" / "trayectorias" / "issue02_planificador.json"),
        herramientas=h,
        politica=Politica(herramientas_permitidas=set(), max_pasos=2),
        objetivo="Elabora un plan breve de 4 pasos para resolver issues/ISSUE-02.md.",
        traza_archivo=traza_plan,
    )
    plan = planificador.ejecutar()
    trazas.append(traza_plan)
    print(f"--- PLANIFICADOR ---\n{plan}\n")

    retro = ""
    for ronda in range(1, MAX_RONDAS + 1):
        traza_ej = RAIZ / "agentes" / "trazas" / f"issue02_ejecutor_r{ronda}.jsonl"
        ejecutor = Agente(
            nombre=f"ejecutor_r{ronda}",
            modelo=ModeloGrabado(RAIZ / "agentes" / "trayectorias" / f"issue02_ejecutor_r{ronda}.json"),
            herramientas=h,
            politica=Politica(max_pasos=12, aprobar_edicion=aprobar_edicion),
            objetivo=f"Resuelve issues/ISSUE-02.md siguiendo este plan:\n{plan}\n{retro}Herramientas: {h.catalogo()}",
            traza_archivo=traza_ej,
        )
        resumen = ejecutor.ejecutar()
        trazas.append(traza_ej)

        traza_rev = RAIZ / "agentes" / "trazas" / f"issue02_revisor_r{ronda}.jsonl"
        revisor = Agente(
            nombre=f"revisor_r{ronda}",
            modelo=ModeloGrabado(RAIZ / "agentes" / "trayectorias" / f"issue02_revisor_r{ronda}.json"),
            herramientas=h,
            politica=Politica(
                herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar", "ejecutar_pruebas"},
                max_pasos=8,
            ),
            objetivo=f"Revisa el cambio del ejecutor. Responde APROBADO o CAMBIOS SOLICITADOS.\nResumen:\n{resumen}",
            traza_archivo=traza_rev,
        )
        veredicto = revisor.ejecutar()
        trazas.append(traza_rev)
        print(f"--- RONDA {ronda} ---\nEJECUTOR: {resumen}\nREVISOR: {veredicto}\n")

        if not veredicto.startswith("CAMBIOS SOLICITADOS"):
            break
        retro = f"El revisor solicitó cambios:\n{veredicto}\n"

    print("Decisión final: HUMANO (aprobar o rechazar el PR).")
    return trazas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=["unico", "actor-critico"], default="actor-critico")
    parser.add_argument(
        "--sin-confirmacion",
        action="store_true",
        help="Desactiva la confirmación interactiva (solo para CI o demos no interactivas)",
    )
    args = parser.parse_args()
    h = Herramientas(RAIZ)
    aprobador = None if args.sin_confirmacion else solicitar_aprobacion_consola

    if args.modo == "unico":
        trazas = ejecutar_unico(h, aprobar_edicion=aprobador)
        salida_mmd = RAIZ / "agentes" / "trazas" / "issue02_unico.mmd"
    else:
        trazas = ejecutar_actor_critico(h, aprobar_edicion=aprobador)
        salida_mmd = RAIZ / "agentes" / "trazas" / "issue02_actor_critico.mmd"

    eventos = cargar_eventos(trazas)
    salida_mmd.write_text(generar_mermaid(eventos), encoding="utf-8")
    print("Métricas consolidadas:", resumir_metricas(eventos))


if __name__ == "__main__":
    main()
