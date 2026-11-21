from src.sancamilo.pedidos.totales import LineaMonto, calcular_total_soles


def test_issue_03_redondeo_exacto_en_centimos():
    # Con float: 2.675 -> "2.67" por representación binaria; con Decimal ROUND_HALF_UP -> "2.68"
    lineas = [
        LineaMonto(nombre="Especias a granel", cantidad=1, precio_unitario="2.675"),
    ]
    assert calcular_total_soles(lineas) == "2.68"


def test_issue_03_suma_decimal_con_descuento():
    lineas = [
        LineaMonto(nombre="Ají panca", cantidad=3, precio_unitario="0.10"),
        LineaMonto(nombre="Cebolla roja", cantidad=1, precio_unitario="1.005"),
    ]
    # 0.30 + 1.005 - 0.10 = 1.205 -> ROUND_HALF_UP => "1.21"
    assert calcular_total_soles(lineas, descuento="0.10") == "1.21"
