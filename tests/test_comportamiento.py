"""Pruebas de caracterización (red de seguridad) para antes y después del refactor."""

import importlib
import pytest
from src.pedidos.externos import YapeSDK, PlinClient, ClienteLLMFalso


@pytest.fixture(params=["src.pedidos.antes.servicio", "src.pedidos.servicio"])
def m(request):
    return importlib.import_module(request.param)


def crear_pedido_multipuesto(m, precio: float = 10.0, cantidad: int = 2, modalidad: str = "RECOJO"):
    return m.Pedido(
        id=101,
        celular="959111222",
        modalidad=modalidad,
        lineas=[
            m.Linea("Papa Amarilla", cantidad, precio, puesto="Puesto 12 - Verduras"),
            m.Linea("Queso Paria", 1, 15.0, puesto="Puesto 45 - Lácteos"),
        ],
    )


def test_01_pago_yape_aprobado_notifica_puestos_y_reporte(m):
    s = m.ServicioPedidos()
    p = crear_pedido_multipuesto(m, precio=10.0, cantidad=2)  # Total = 35.00
    assert s.confirmar_y_pagar(p, "YAPE") == "PAGADO"
    assert p.operacion == "YAPE-3500"
    assert s.eventos == [
        "whatsapp:Puesto 12 - Verduras:Pedido 101 pagado",
        "whatsapp:Puesto 45 - Lácteos:Pedido 101 pagado",
        "reporte:101:35.00",
    ]


def test_02_pago_plin_con_delivery_suma_tarifa(m):
    s = m.ServicioPedidos()
    p = crear_pedido_multipuesto(m, precio=10.0, cantidad=2, modalidad="DELIVERY")  # 35 + 5 = 40.00
    assert s.confirmar_y_pagar(p, "PLIN") == "PAGADO"
    assert p.operacion == "PLIN-4000"
    assert "reporte:101:40.00" in s.eventos


def test_03_reintenta_dos_timeouts_y_aprueba_en_tercer_intento(m):
    yape = YapeSDK(fallas=2)
    s = m.ServicioPedidos(yape=yape)
    assert s.confirmar_y_pagar(crear_pedido_multipuesto(m), "YAPE") == "PAGADO"
    assert yape.llamadas == 3


def test_04_tres_timeouts_cancela_pedido_sin_eventos(m):
    yape = YapeSDK(fallas=3)
    s = m.ServicioPedidos(yape=yape)
    p = crear_pedido_multipuesto(m)
    assert s.confirmar_y_pagar(p, "YAPE") == "CANCELADO"
    assert s.eventos == []


def test_05_monto_sobre_limite_cancela_sin_reintentar(m):
    yape = YapeSDK(limite=100.0)
    s = m.ServicioPedidos(yape=yape)
    p = crear_pedido_multipuesto(m, precio=60.0, cantidad=2)  # Total 135.0 > 100.0
    assert s.confirmar_y_pagar(p, "YAPE") == "CANCELADO"
    assert yape.llamadas == 1
    assert s.eventos == []


def test_06_error_si_pedido_sin_lineas(m):
    s = m.ServicioPedidos()
    p = m.Pedido(id=102, celular="959111222", lineas=[])
    with pytest.raises(ValueError, match="no tiene líneas"):
        s.confirmar_y_pagar(p, "YAPE")


def test_07_error_si_pedido_ya_estaba_pagado(m):
    s = m.ServicioPedidos()
    p = crear_pedido_multipuesto(m)
    s.confirmar_y_pagar(p, "YAPE")
    with pytest.raises(ValueError, match="ya fue pagado"):
        s.confirmar_y_pagar(p, "YAPE")


def test_08_medio_no_soportado_lanza_error_y_conserva_borrador(m):
    s = m.ServicioPedidos()
    p = crear_pedido_multipuesto(m)
    with pytest.raises(ValueError, match="Medio de pago no soportado"):
        s.confirmar_y_pagar(p, "BITCOIN")
    assert p.estado == "BORRADOR"


def test_09_ia_normaliza_producto_y_usa_cache(m):
    llm = ClienteLLMFalso("Papa Amarilla Tumbay (Kg)")
    s = m.ServicioPedidos(llm=llm)
    assert s.normalizar_producto("  papa amarila ") == "Papa Amarilla Tumbay (Kg)"
    assert s.normalizar_producto("PAPA AMARILA") == "Papa Amarilla Tumbay (Kg)"
    assert llm.llamadas == 1


def test_10_ia_bloquea_precio_infiltrado_en_nombre(m):
    llm = ClienteLLMFalso("Papa Amarilla a solo S/ 3.50 el kilo")
    s = m.ServicioPedidos(llm=llm)
    with pytest.raises(ValueError, match="Guardrail"):
        s.normalizar_producto("papa amarilla")