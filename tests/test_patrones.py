"""Pruebas específicas que demuestran cada patrón de diseño GoF aplicado."""

import pytest
from src.pedidos.pagos import PasarelaPago, ResultadoPago
from src.pedidos.servicio import ServicioPedidos, Pedido, Linea


def crear_pedido_base() -> Pedido:
    return Pedido(
        id=201,
        celular="959000999",
        lineas=[Linea("Rocoto Relleno", 2, 12.50, puesto="Puesto 08 - Tradicional")],
    )


def test_e2_open_closed_nueva_pasarela_sin_modificar_servicio():
    class CulqiQRAdapter(PasarelaPago):
        def cobrar(self, monto: float, celular: str) -> ResultadoPago:
            return ResultadoPago(aprobado=True, operacion=f"CULQI-{int(monto)}")

    servicio = ServicioPedidos()
    servicio.fabrica.registrar("CULQI_QR", CulqiQRAdapter)

    pedido = crear_pedido_base()
    estado = servicio.confirmar_y_pagar(pedido, "CULQI_QR")

    assert estado == "PAGADO"
    assert pedido.operacion == "CULQI-25"

def test_e3_state_impide_pagar_sin_confirmar_o_cancelar_un_pedido_pagado():
    pedido = crear_pedido_base()
    # No se puede pagar directamente desde BORRADOR sin confirmar primero
    with pytest.raises(ValueError, match="No se puede pagar un pedido en estado BORRADOR"):
        pedido.pagar("YAPE-100")

    # Flujo válido: BORRADOR -> CONFIRMADO -> PAGADO
    pedido.confirmar()
    assert pedido.estado == "CONFIRMADO"
    pedido.pagar("YAPE-2500")
    assert pedido.estado == "PAGADO"

    # Una vez PAGADO no se puede cancelar ni volver a pagar
    with pytest.raises(ValueError, match="No se puede cancelar un pedido en estado PAGADO"):
        pedido.cancelar()