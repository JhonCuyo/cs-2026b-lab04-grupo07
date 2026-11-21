from src.sancamilo.catalogo.productos import ProductoCatalogo, listar_productos_visibles


def test_issue_02_producto_agotado_no_es_visible():
    productos = [
        ProductoCatalogo(id="P1", nombre="Rocoto arequipeño", puesto="A-01", precio=5.0, stock=10, activo=True),
        ProductoCatalogo(id="P2", nombre="Palta fuerte", puesto="A-02", precio=9.0, stock=0, activo=True),
        ProductoCatalogo(id="P3", nombre="Choclo desgranado", puesto="A-03", precio=6.0, stock=4, activo=False),
    ]
    visibles = listar_productos_visibles(productos)
    assert [p.id for p in visibles] == ["P1"]
