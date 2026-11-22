"""Política de guardrails y mínimo privilegio por rol de agente."""

from dataclasses import dataclass, field
import re
from typing import Callable


@dataclass(frozen=True)
class Decision:
    permitido: bool
    motivo: str = ""


@dataclass
class Politica:
    herramientas_permitidas: set[str] = field(
        default_factory=lambda: {
            "listar_archivos",
            "leer_archivo",
            "buscar",
            "ejecutar_pruebas",
            "editar_archivo",
            "ver_cambios",
            "ejecutar_comando",
            "mapa_repo",
            "anotar",
            "leer_notas",
        }
    )
    comandos_permitidos: tuple[str, ...] = (
        r"^python -m pytest\b",
        r"^radon cc\b",
        r"^lint-imports\b",
        r"^git (status|diff)\b",
    )
    rutas_protegidas: tuple[str, ...] = ("tests/", "agentes/pruebas_agente/")
    max_pasos: int = 12
    aprobar_edicion: Callable[[dict], bool] | None = None

    def evaluar(self, accion: str, args: dict, paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando":
            cmd = args.get("comando", "")
            if not any(re.search(p, cmd) for p in self.comandos_permitidos):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = args.get("ruta", "")
            if ruta.startswith(self.rutas_protegidas):
                return Decision(False, f"Ruta protegida: {ruta}")
            if self.aprobar_edicion and not self.aprobar_edicion(args):
                return Decision(False, "El revisor humano rechazó la edición")
        return Decision(True)


def solicitar_aprobacion_consola(args: dict, entrada=input) -> bool:
    """Pide confirmación para una edición y solo la aprueba con 's'."""
    ruta = args.get("ruta", "(desconocida)")
    print(f"\n[HUMANO EN EL CIRCUITO] El agente propone editar: {ruta}")
    print(f"--- ANTES ---\n{args.get('antes', '')}")
    print(f"--- DESPUÉS ---\n{args.get('despues', '')}")
    while True:
        try:
            respuesta = entrada("¿Aprobar esta edición? (s/n): ").strip().lower()
        except EOFError:
            print("No se recibió confirmación. Edición rechazada.")
            return False
        if respuesta in ("s", "n"):
            return respuesta == "s"
        print("Entrada inválida. Responda únicamente 's' o 'n'.")
