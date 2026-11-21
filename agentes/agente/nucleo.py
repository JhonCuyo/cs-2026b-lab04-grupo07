"""Núcleo del agente: bucle ReAct modelado como máquina de estados con trazas JSONL."""

import json
import pathlib
import time

from agentes.agente.contrato import validar_decision


class Agente:
    def __init__(self, nombre: str, modelo, herramientas, politica, objetivo: str, traza_archivo: str | pathlib.Path):
        self.nombre = nombre
        self.modelo = modelo
        self.h = herramientas
        self.politica = politica
        self.traza_archivo = pathlib.Path(traza_archivo)
        self.traza_archivo.parent.mkdir(parents=True, exist_ok=True)
        self.historial: list[dict] = [{"role": "user", "content": objetivo}]
        self.eventos: list[dict] = []
        self._t0 = 0.0

    def _registrar(self, **campos) -> None:
        campos["agente"] = self.nombre
        campos["t_ms"] = round((time.perf_counter() - self._t0) * 1000, 2)
        campos["contexto_chars"] = sum(len(m["content"]) for m in self.historial)
        self.eventos.append(campos)

    def ejecutar(self) -> str:
        self._t0 = time.perf_counter()
        self._registrar(tipo="objetivo", estado="INICIO", texto=self.historial[0]["content"])
        conocidas = set(self.h.catalogo())

        for paso in range(1, self.politica.max_pasos + 2):
            d = self.modelo.decidir(self.historial)  # DECIDIENDO
            self.historial.append({"role": "assistant", "content": json.dumps(d, ensure_ascii=False)})
            ok, motivo = validar_decision(d, conocidas)  # VALIDANDO_CONTRATO
            if not ok:
                obs = f"ERROR DE CONTRATO: {motivo}. Responda solo con el JSON del protocolo."
                self._registrar(
                    tipo="accion",
                    estado="CONTRATO_INVALIDO",
                    paso=paso,
                    pensamiento=str(d)[:200],
                    accion="(ninguna)",
                    args={},
                    observacion=obs,
                    bloqueada=True,
                )
            elif "final" in d:
                self._registrar(
                    tipo="final",
                    estado="FINALIZADO",
                    paso=paso,
                    pensamiento=d["pensamiento"],
                    texto=d["final"],
                )
                break
            else:
                accion, args = d["accion"], d.get("args", {})
                veredicto = self.politica.evaluar(accion, args, paso)  # EVALUANDO_POLITICA
                if veredicto.permitido:
                    try:
                        obs = getattr(self.h, accion)(**args)  # EJECUTANDO
                    except Exception as e:
                        obs = f"ERROR: {type(e).__name__}: {e}"
                    self._registrar(
                        tipo="accion",
                        estado="OBSERVANDO",
                        paso=paso,
                        pensamiento=d["pensamiento"],
                        accion=accion,
                        args=args,
                        observacion=str(obs)[:600],
                        bloqueada=False,
                    )
                else:
                    obs = f"BLOQUEADO POR LA POLÍTICA: {veredicto.motivo}"
                    limite = "máximo" in veredicto.motivo
                    self._registrar(
                        tipo="accion",
                        estado="LIMITE_ALCANZADO" if limite else "BLOQUEADO",
                        paso=paso,
                        pensamiento=d["pensamiento"],
                        accion=accion,
                        args=args,
                        observacion=obs,
                        bloqueada=True,
                    )
                    if limite:
                        break
            self.historial.append({"role": "user", "content": f"Observación: {obs}"})  # OBSERVANDO -> DECIDIENDO

        with open(self.traza_archivo, "w", encoding="utf-8") as f:
            for e in self.eventos:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        return self.eventos[-1].get("texto", "(sin respuesta final)")
