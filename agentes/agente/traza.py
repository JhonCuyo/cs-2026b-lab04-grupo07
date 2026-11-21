"""Convierte trazas JSONL en un diagrama de secuencia Mermaid y calcula métricas."""

import json
import pathlib
import sys


def cargar_eventos(rutas: list[pathlib.Path]) -> list[dict]:
    eventos = []
    for ruta in rutas:
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                eventos.append(json.loads(linea))
    return eventos


def generar_mermaid(eventos: list[dict]) -> str:
    lineas = [
        "sequenceDiagram",
        "    autonumber",
        "    actor H as Humano",
        "    participant A as Agente",
        "    participant P as Contrato/Política",
        "    participant T as Herramientas",
    ]
    for ev in eventos:
        tipo = ev.get("tipo")
        agente = ev.get("agente", "Agente")
        if tipo == "objetivo":
            lineas.append(f"    H->>A: objetivo ({agente})")
        elif tipo == "accion":
            accion = ev.get("accion", "?")
            if ev.get("bloqueada"):
                estado = ev.get("estado", "BLOQUEADO")
                lineas.append(f"    A-xP: {accion} [{estado}]")
                lineas.append(f"    P-->>A: {estado}")
            else:
                lineas.append(f"    A->>T: {accion}")
                obs = ev.get("observacion", "").replace("\n", " ")[:45]
                lineas.append(f"    T-->>A: {obs}")
        elif tipo == "final":
            lineas.append(f"    A-->>H: respuesta final ({agente})")
    return "\n".join(lineas) + "\n"


def resumir_metricas(eventos: list[dict]) -> dict:
    acciones = [e for e in eventos if e.get("tipo") == "accion"]
    contrato_inv = sum(1 for e in acciones if e.get("estado") == "CONTRATO_INVALIDO")
    bloqueadas = sum(1 for e in acciones if e.get("bloqueada") and e.get("estado") != "CONTRATO_INVALIDO")
    herramientas = sorted({e["accion"] for e in acciones if not e.get("bloqueada")})
    contexto_max = max((e.get("contexto_chars", 0) for e in eventos), default=0)
    return {
        "pasos": len(acciones),
        "contrato_invalido": contrato_inv,
        "bloqueadas_politica": bloqueadas,
        "herramientas": herramientas,
        "contexto_max_chars": contexto_max,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python agentes/agente/traza.py <traza1.jsonl> [traza2.jsonl ...] [-o salida.mmd]")
        sys.exit(1)
    args = sys.argv[1:]
    salida = None
    if "-o" in args:
        idx = args.index("-o")
        salida = pathlib.Path(args[idx + 1])
        args = args[:idx] + args[idx + 2:]
    rutas = [pathlib.Path(a) for a in args]
    evs = cargar_eventos(rutas)
    mmd = generar_mermaid(evs)
    destino = salida or rutas[0].with_suffix(".mmd")
    destino.write_text(mmd, encoding="utf-8")
    print(f"Diagrama generado en {destino}")
    print("Métricas:", json.dumps(resumir_metricas(evs), ensure_ascii=False))
