"""Tácticas de Disponibilidad (Iteración 3 - QA-04):
Reintentos + Circuit Breaker (Decorator sobre PasarelaPago) + Cola Outbox en PostgreSQL.
"""

import random
import time
from src.pedidos.pagos import PasarelaPago, ResultadoPago


class CircuitoAbiertoError(Exception):
    """Falla rápida: el circuito está abierto y el pago pasa a la tabla outbox_pagos."""


class ConCircuitBreaker(PasarelaPago):
    """Decorator (Lab 07 -> Lab 08): envuelve una PasarelaPago con un Circuit Breaker."""

    def __init__(self, interna: PasarelaPago, umbral: int = 3, espera_s: float = 120.0, reloj=time.monotonic):
        self._interna = interna
        self._umbral = umbral
        self._espera_s = espera_s
        self._reloj = reloj
        self._fallas = 0
        self._abierto_desde: float | None = None

    @property
    def estado(self) -> str:
        if self._abierto_desde is None:
            return "CERRADO"
        if (self._reloj() - self._abierto_desde) >= self._espera_s:
            return "SEMIABIERTO"
        return "ABIERTO"

    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        if self.estado == "ABIERTO":
            raise CircuitoAbiertoError("Proveedor de pagos caído: cobro diferido a tabla outbox")
        try:
            resultado = self._interna.cobrar(monto, celular)
        except TimeoutError:
            self._registrar_falla()
            raise
        self._fallas = 0
        self._abierto_desde = None
        return resultado

    def _registrar_falla(self) -> None:
        self._fallas += 1
        if self._fallas >= self._umbral or self.estado == "SEMIABIERTO":
            self._abierto_desde = self._reloj()


def simular(modo: str, pedidos_totales: int = 1800, semilla: int = 42) -> dict:
    """Simula una jornada de 10 horas (600 min = 36000 s, 1 pedido cada 20 s = 1800 pedidos).
    - Hay 8% de probabilidad de timeout transitorio de red.
    - Entre el minuto 180 y 200 (20 min = 60 pedidos) el proveedor Yape cae al 100%.
    Modos: 'sin_tacticas', 'reintentos', 'breaker' (reintentos + circuit breaker + outbox PostgreSQL).
    """
    rnd = random.Random(semilla)
    caida_inicio, caida_fin = 180 * 60, 200 * 60
    reloj_sim = [0.0]

    class PasarelaSimulada(PasarelaPago):
        def __init__(self):
            self.llamadas_en_caida = 0

        def cobrar(self, monto: float, celular: str) -> ResultadoPago:
            t = reloj_sim[0]
            en_caida = caida_inicio <= t < caida_fin
            if en_caida:
                self.llamadas_en_caida += 1
                raise TimeoutError("Caída total de Yape API (20 min)")
            if rnd.random() < 0.08:
                raise TimeoutError("Falla transitoria de red")
            return ResultadoPago(aprobado=True, operacion="YAPE-OK")

    sdk = PasarelaSimulada()
    breaker = ConCircuitBreaker(sdk, umbral=3, espera_s=120.0, reloj=lambda: reloj_sim[0])

    completados = 0
    en_outbox = 0

    for i in range(pedidos_totales):
        reloj_sim[0] = float(i * 20)

        if modo == "sin_tacticas":
            try:
                sdk.cobrar(35.0, "959000111")
                completados += 1
            except TimeoutError:
                pass

        elif modo == "reintentos":
            for _ in range(3):
                try:
                    sdk.cobrar(35.0, "959000111")
                    completados += 1
                    break
                except TimeoutError:
                    continue

        elif modo == "breaker":
            for _ in range(3):
                try:
                    breaker.cobrar(35.0, "959000111")
                    completados += 1
                    break
                except CircuitoAbiertoError:
                    en_outbox += 1
                    break
                except TimeoutError:
                    if breaker.estado == "ABIERTO":
                        en_outbox += 1
                        break

    # El Worker Celery procesa la tabla outbox en PostgreSQL una vez que Yape vuelve a estar en línea
    completados_finales = completados + en_outbox
    perdidos = pedidos_totales - completados_finales

    return {
        "modo": modo,
        "pedidos_totales": pedidos_totales,
        "completados": completados_finales,
        "diferidos_outbox": en_outbox,
        "perdidos": perdidos,
        "llamadas_en_caida": sdk.llamadas_en_caida,
    }


def generar_grafico_iteracion3(ruta_salida: str = "docs/architecture/add/disponibilidad_iteracion3.png") -> None:
    import matplotlib.pyplot as plt

    modos = [("Sin tácticas", "sin_tacticas", "#C0392B"), ("Solo Reintentos (3)", "reintentos", "#F39C12"), ("Reintentos + Breaker\n+ Outbox BD", "breaker", "#27AE60")]
    resultados = [(etiqueta, simular(clave), color) for etiqueta, clave, color in modos]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))

    etiquetas = [r[0] for r in resultados]
    perdidos = [r[1]["perdidos"] for r in resultados]
    colores = [r[2] for r in resultados]

    b1 = ax1.bar(etiquetas, perdidos, color=colores, width=0.5)
    for b, r in zip(b1, resultados):
        pct = (r[1]["completados"] / r[1]["pedidos_totales"]) * 100
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 4, f"{r[1]['perdidos']} perdidos\n({pct:.1f}% éxito)", ha="center", fontsize=8.5)
    ax1.set_ylim(0, max(perdidos) * 1.25)
    ax1.set_ylabel("Pedidos perdidos en la jornada")
    ax1.set_title("Pedidos perdidos (1800 pedidos, caída de 20 min)")

    llamadas = [r[1]["llamadas_en_caida"] for r in resultados]
    b2 = ax2.bar(etiquetas, llamadas, color=colores, width=0.5)
    for b in b2:
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 3, f"{int(b.get_height())}", ha="center", fontsize=9, fontweight="bold")
    ax2.set_ylim(0, max(llamadas) * 1.2)
    ax2.set_ylabel("Llamadas a Yape durante su caída de 20 min")
    ax2.set_title("Protección al proveedor y workers durante la caída")

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=160)
    plt.close()


if __name__ == "__main__":
    for m in ("sin_tacticas", "reintentos", "breaker"):
        print(simular(m))
    generar_grafico_iteracion3()