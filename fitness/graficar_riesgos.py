"""Genera el gráfico de la Matriz de Probabilidad e Impacto de los riesgos ATAM-lite (E7)."""

import matplotlib.pyplot as plt


def generar_matriz_riesgos(ruta_salida: str = "docs/architecture/riesgos_atam.png") -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))

    # Sombrear zonas
    ax.axhspan(3.5, 5.3, xmin=0.45, xmax=1.0, color="#FADBD8", alpha=0.55, label="Zona crítica (Mitigar)")
    ax.axhspan(0.7, 3.5, xmin=0.0, xmax=0.45, color="#D5F5E3", alpha=0.45, label="Zona aceptable")

    riesgos = [
        (2.0, 4.8, "R1: VPS único (SPOF)\n[Aceptado en MVP + Backup diario]", "#C0392B"),
        (3.0, 5.0, "R2: Error en políticas RLS expone\ndatos de otro mercado [Mitigado FF-06]", "#8E44AD"),
        (3.1, 3.9, "R3: Pagos diferidos en Redis sin\npersistencia [Mitigado: Outbox en BD]", "#D35400"),
        (4.0, 2.2, "R4: Caché muestra stock con 30s\nde desfase [Mitigado: TTL 30s + TX]", "#2980B9"),
        (3.0, 1.8, "R5: Conflicto de edición offline 3G\n[Mitigado: Last-Write-Wins]", "#27AE60"),
    ]

    for prob, imp, texto, color in riesgos:
        ax.scatter(prob, imp, s=140, color=color, zorder=5)
        ax.annotate(texto, (prob, imp), textcoords="offset points", xytext=(10, -6), fontsize=8.5, fontweight="bold")

    ax.set_xlim(1, 5.3)
    ax.set_ylim(1, 5.4)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_xlabel("Probabilidad (1 = muy baja ... 5 = muy alta)")
    ax.set_ylabel("Impacto en los escenarios de calidad (1 .. 5)")
    ax.set_title("Matriz de Riesgos Arquitectónicos ATAM-lite — San Camilo en Línea 2.0")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower left", fontsize=8.5)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=160)
    plt.close()


if __name__ == "__main__":
    generar_matriz_riesgos()