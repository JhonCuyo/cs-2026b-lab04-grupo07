"""Cálculo de totales monetarios en soles para San Camilo en Línea."""

from dataclasses import dataclass


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
    # ERROR SEMBRADO (ISSUE-03): usa aritmética float binaria sin redondeo Decimal HALF_UP
    subtotal = sum(linea.cantidad * float(linea.precio_unitario) for linea in lineas)
    total = subtotal - float(descuento)
    return f"{total:.2f}"
