from src.sancamilo.pedidos.comisiones import ItemPedido, calcular_comision_pedido


def test_issue_01_pedido_multipuesto_cobra_una_sola_comision():
    items = [
        ItemPedido(puesto="Puesto A-12", producto="Papa amarilla", cantidad=2, precio_unitario=4.50),
        ItemPedido(puesto="Puesto B-05", producto="Queso helado", cantidad=1, precio_unitario=8.00),
    ]
    assert calcular_comision_pedido(items) == 2.50


def test_issue_01_pedido_vacio_sin_comision():
    assert calcular_comision_pedido([]) == 0.0
