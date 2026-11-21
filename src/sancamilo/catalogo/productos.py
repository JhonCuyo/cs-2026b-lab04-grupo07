"""Consultas del catálogo visible para clientes de San Camilo en Línea."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductoCatalogo:
    id: str
    nombre: str
    puesto: str
    precio: float
    stock: int
    activo: bool = True


def listar_productos_visibles(productos: list[ProductoCatalogo]) -> list[ProductoCatalogo]:
    """Devuelve los productos que deben mostrarse al cliente en la PWA.

    Regla de negocio: solo deben mostrarse productos activos y con stock > 0.
    """
    return [p for p in productos if p.activo is True and p.stock > 0]
