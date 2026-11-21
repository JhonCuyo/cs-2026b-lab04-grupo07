"""Cálculo de totales monetarios en soles para San Camilo en Línea."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class LineaMonto:
    nombre: str
    cantidad: int
    precio_unitario: str  # Ej: "0.10", "3.35"


def calcular_total_soles(lineas: list[LineaMonto], descuento: str = "0.00") -> str:
    """Suma las líneas del pedido, aplica descuento y devuelve el monto exacto a 2 decimales.

    Regla de negocio: usar aritmética decimal exacta con redondeo comercial (HALF_UP)
    para evitar errores binarios de punto flotante en céntimos.
    """
    subtotal = sum(
        (Decimal(linea.precio_unitario) * linea.cantidad for linea in lineas),
        Decimal("0"),
    )
    total = subtotal - Decimal(descuento)
    return str(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
