"""Implementaciones Strategy de la interfaz Modelo (Grabado e Interactivo)."""

import json
import pathlib


class ModeloGrabado:
    """Reproduce una lista de decisiones JSON grabadas previamente."""

    def __init__(self, ruta_json: str | pathlib.Path):
        self.ruta = pathlib.Path(ruta_json)
        self.decisiones = json.loads(self.ruta.read_text(encoding="utf-8"))
        self._indice = 0

    def decidir(self, historial: list[dict]):
        if self._indice >= len(self.decisiones):
            return {
                "pensamiento": "No hay más decisiones grabadas.",
                "final": "Fin de trayectoria grabada.",
            }
        d = self.decisiones[self._indice]
        self._indice += 1
        return d


class ModeloInteractivo:
    """Permite operar con un asistente de IA en el navegador y grabar la trayectoria."""

    def __init__(self, ruta_salida: str | pathlib.Path):
        self.ruta_salida = pathlib.Path(ruta_salida)
        self.ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        self.grabadas: list = []

    def decidir(self, historial: list[dict]):
        print("\n" + "=" * 60)
        print("ÚLTIMO MENSAJE PARA EL ASISTENTE DE IA:")
        print(historial[-1]["content"])
        print("=" * 60)
        bruto = input("Pega la respuesta JSON del asistente (una línea): ").strip()
        try:
            decision = json.loads(bruto)
        except json.JSONDecodeError:
            decision = bruto  # Se entrega tal cual para que el contrato lo rechace
        self.grabadas.append(decision)
        self.ruta_salida.write_text(
            json.dumps(self.grabadas, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return decision
