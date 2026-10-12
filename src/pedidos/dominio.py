from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class EstadoPedido(Enum):
    BORRADOR = "BORRADOR"
    CONFIRMADO = "CONFIRMADO"
    PAGO_PENDIENTE = "PAGO_PENDIENTE"
    PAGADO = "PAGADO"
    EN_PREPARACION = "EN_PREPARACION"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class EstadoPedidoPuesto(Enum):
    RECIBIDO = "RECIBIDO"
    LISTO = "LISTO"
    RECOGIDO = "RECOGIDO"


class MedioPago(Enum):
    YAPE = "YAPE"
    PLIN = "PLIN"


@dataclass
class Producto:
    id: UUID
    nombre: str
    precio_unitario: Decimal
    stock_disponible: int

    def reservar(self, cantidad: int) -> None:
        if cantidad > self.stock_disponible:
            raise ValueError("Stock insuficiente")
        self.stock_disponible -= cantidad

    def liberar(self, cantidad: int) -> None:
        self.stock_disponible += cantidad


@dataclass
class LineaPedido:
    cantidad: int
    precio_unitario: Decimal
    producto: Producto

    def subtotal(self) -> Decimal:
        return self.precio_unitario * Decimal(self.cantidad)


@dataclass
class Pago:
    id: UUID
    monto: Decimal
    medio: MedioPago
    codigo_operacion: str
    aprobado: bool


@dataclass
class PedidoPuesto:
    id: UUID
    estado_puesto: EstadoPedidoPuesto = EstadoPedidoPuesto.RECIBIDO

    def marcar_listo(self) -> None:
        self.estado_puesto = EstadoPedidoPuesto.LISTO


@dataclass
class PedidoMultipuesto:
    id: UUID = field(default_factory=uuid4)
    fecha: datetime = field(default_factory=datetime.now)
    total: Decimal = Decimal("0.00")
    estado: EstadoPedido = EstadoPedido.BORRADOR
    lineas: list[LineaPedido] = field(default_factory=list)
    pedidos_puesto: list[PedidoPuesto] = field(default_factory=list)
    pago: Optional[Pago] = None

    def agregar_linea(self, producto: Producto, cantidad: int) -> None:
        linea = LineaPedido(cantidad=cantidad, precio_unitario=producto.precio_unitario, producto=producto)
        self.lineas.append(linea)

    def calcular_total(self) -> Decimal:
        self.total = sum((linea.subtotal() for linea in self.lineas), Decimal("0.00"))
        return self.total

    def confirmar(self) -> None:
        if not self.lineas:
            raise ValueError("El pedido debe contener al menos una linea (Regla C3)")
        for linea in self.lineas:
            linea.producto.reservar(linea.cantidad)
        self.estado = EstadoPedido.CONFIRMADO

    def registrar_pago(self, pago: Pago) -> None:
        self.pago = pago
        if pago.aprobado:
            self.estado = EstadoPedido.PAGADO

    def cancelar(self, motivo: str) -> None:
        for linea in self.lineas:
            linea.producto.liberar(linea.cantidad)
        self.estado = EstadoPedido.CANCELADO


class PasarelaPago(ABC):
    @abstractmethod
    def cobrar(self, monto: Decimal, celular: str) -> Pago:
        pass


class YapeAdapter(PasarelaPago):
    def cobrar(self, monto: Decimal, celular: str) -> Pago:
        raise NotImplementedError("Integracion con la API de Yape")


class PlinAdapter(PasarelaPago):
    def cobrar(self, monto: Decimal, celular: str) -> Pago:
        raise NotImplementedError("Integracion con la API de Plin")