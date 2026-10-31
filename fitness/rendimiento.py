"""Simulación de colas M/G/c para la Iteración 2 de ADD (QA-03: 18 req/s en 3 mercados)."""

import heapq
import math
import random
import statistics


def bd_sin_indice(rnd: random.Random) -> float:
    """Consulta de catálogo multimercado sin índice compuesto (media ~240 ms)."""
    return rnd.lognormvariate(math.log(0.22), 0.35)


def bd_con_indice(rnd: random.Random) -> float:
    """Consulta con índice compuesto (mercado_id, puesto_id) en PostgreSQL (media ~42 ms)."""
    return rnd.lognormvariate(math.log(0.038), 0.30)


def con_cache(servicio_bd, hit_rate: float = 0.85):
    """Táctica Caché en Redis (acierto ~4 ms; fallo va a la BD)."""
    def _servicio(rnd: random.Random) -> float:
        if rnd.random() < hit_rate:
            return rnd.lognormvariate(math.log(0.004), 0.20)
        return servicio_bd(rnd)
    return _servicio


def simular(lam: float, workers: int, servicio, segundos: int = 120, semilla: int = 7) -> dict:
    """Simula un sistema de colas M/G/c durante 'segundos' con tasa de llegada 'lam' (req/s)."""
    rnd = random.Random(semilla)
    t, llegadas = 0.0, []
    while t < segundos:
        t += rnd.expovariate(lam)
        llegadas.append(t)

    libres = [0.0] * workers
    heapq.heapify(libres)
    respuestas_ms: list[float] = []

    for llegada in llegadas:
        libre = heapq.heappop(libres)
        inicio = max(llegada, libre)
        fin = inicio + servicio(rnd)
        heapq.heappush(libres, fin)
        respuestas_ms.append((fin - llegada) * 1000.0)

    respuestas_ms.sort()
    percentil = lambda q: respuestas_ms[int(q * (len(respuestas_ms) - 1))]
    return {
        "n": len(respuestas_ms),
        "p50": round(percentil(0.50), 1),
        "p95": round(percentil(0.95), 1),
        "media": round(statistics.mean(respuestas_ms), 1),
    }


def generar_grafico_iteracion2(ruta_salida: str = "docs/architecture/add/rendimiento_iteracion2.png") -> None:
    import matplotlib.pyplot as plt

    cargas = [("Normal\n(6 req/s)", 6), ("1 Mercado Pico\n(12 req/s)", 12), ("3 Mercados Pico\n(18 req/s)", 18)]
    estrategias = [
        ("Sin tácticas (4 workers)", lambda lam: simular(lam, 4, bd_sin_indice)["p95"], "#C0392B"),
        ("Escalar a 8 workers (2 VPS)", lambda lam: simular(lam, 8, bd_sin_indice)["p95"], "#7F8C8D"),
        ("Índice compuesto en BD", lambda lam: simular(lam, 4, bd_con_indice)["p95"], "#F39C12"),
        ("Solo Caché (85% hit)", lambda lam: simular(lam, 4, con_cache(bd_sin_indice, 0.85))["p95"], "#2980B9"),
        ("Índice + Caché (Adoptada)", lambda lam: simular(lam, 4, con_cache(bd_con_indice, 0.85))["p95"], "#27AE60"),
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    x = range(len(cargas))
    ancho = 0.16
    for i, (nombre, fn, color) in enumerate(estrategias):
        valores = [fn(lam) for _, lam in cargas]
        pos = [p + (i - 2) * ancho for p in x]
        barras = ax1.bar(pos, valores, width=ancho, label=nombre, color=color)
        for b in barras:
            h = b.get_height()
            ax1.text(b.get_x() + b.get_width() / 2, h * 1.05, f"{int(h)}", ha="center", va="bottom", fontsize=7)

    ax1.axhline(1500, color="black", linestyle="--", linewidth=1, label="Meta QA-03: p95 <= 1500 ms")
    ax1.set_yscale("log")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([etiqueta for etiqueta, _ in cargas])
    ax1.set_ylabel("p95 tiempo de respuesta (ms, escala log)")
    ax1.set_title("Tácticas de Rendimiento (San Camilo + Altiplano + Río Seco)")
    ax1.legend(fontsize=7.5, loc="upper left")

    # Curva de sensibilidad del hit rate de la caché a 18 req/s
    tasas = [i / 20.0 for i in range(0, 20)]
    p95_solo_cache = [simular(18, 4, con_cache(bd_sin_indice, hr))["p95"] for hr in tasas]
    p95_indice_cache = [simular(18, 4, con_cache(bd_con_indice, hr))["p95"] for hr in tasas]

    ax2.plot([t * 100 for t in tasas], p95_solo_cache, "o-", color="#2980B9", label="Solo caché (sin índice)")
    ax2.plot([t * 100 for t in tasas], p95_indice_cache, "s-", color="#27AE60", label="Índice + caché (adoptada)")
    ax2.axhline(1500, color="black", linestyle="--", linewidth=1, label="Meta QA-03 (1500 ms)")
    ax2.set_yscale("log")
    ax2.set_xlabel("Tasa de aciertos de caché en Redis (%)")
    ax2.set_ylabel("p95 (ms, escala log) a 18 req/s")
    ax2.set_title("Punto de sensibilidad: Tasa de aciertos de caché (18 req/s)")
    ax2.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=160)
    plt.close()


if __name__ == "__main__":
    print("=== RESULTADOS SIMULACIÓN M/G/c A 18 REQ/S (3 MERCADOS) ===")
    print("  Sin tácticas (4 workers):", simular(18, 4, bd_sin_indice))
    print("  Escalar a 8 workers:     ", simular(18, 8, bd_sin_indice))
    print("  Índice en BD:            ", simular(18, 4, bd_con_indice))
    print("  Solo Caché (85%):        ", simular(18, 4, con_cache(bd_sin_indice, 0.85)))
    print("  Índice + Caché (85%):    ", simular(18, 4, con_cache(bd_con_indice, 0.85)))
    generar_grafico_iteracion2()