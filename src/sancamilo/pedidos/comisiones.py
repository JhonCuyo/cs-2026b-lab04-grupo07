"""Cálculo de comisión de plataforma para pedidos multipuesto de San Camilo en Línea."""

from dataclasses import dataclass

COMISION_FIJA_PEDIDO = 2.50


@dataclass(frozen=True)
class ItemPedido:
    puesto: str
    producto: str
    cantidad: int
    precio_unitario: float


def calcular_comision_pedido(items: list[ItemPedido]) -> float:
    """Calcula la comisión de servicio para un pedido.

    Regla de negocio: la comisión de S/ 2.50 se cobra UNA sola vez por pedido,
    sin importar cuántos puestos del Mercado San Camilo participen.
    """
    if not items:
        return 0.0
    puestos = {item.puesto for item in items}
    # ERROR SEMBRADO (ISSUE-01): multiplica la comisión por la cantidad de puestos
    return COMISION_FIJA_PEDIDO * len(puestos)
