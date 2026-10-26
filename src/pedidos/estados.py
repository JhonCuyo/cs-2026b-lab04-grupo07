"""Patrón State: Máquina de estados del Pedido Multipuesto (Lab 05 -> Lab 07)."""


class EstadoPedido:
    """Clase base State: toda transición no permitida lanza ValueError por defecto."""

    nombre: str = "?"

    def confirmar(self, pedido) -> None:
        raise ValueError(f"No se puede confirmar un pedido en estado {self.nombre}")

    def pagar(self, pedido, operacion: str | None) -> None:
        raise ValueError(f"No se puede pagar un pedido en estado {self.nombre}")

    def cancelar(self, pedido) -> None:
        raise ValueError(f"No se puede cancelar un pedido en estado {self.nombre}")


class Borrador(EstadoPedido):
    nombre = "BORRADOR"

    def confirmar(self, pedido) -> None:
        if not pedido.lineas:
            raise ValueError("El pedido no tiene líneas")
        pedido.cambiar_a(Confirmado())

    def cancelar(self, pedido) -> None:
        pedido.cambiar_a(Cancelado())


class Confirmado(EstadoPedido):
    nombre = "CONFIRMADO"

    def pagar(self, pedido, operacion: str | None) -> None:
        pedido.operacion = operacion
        pedido.cambiar_a(Pagado())

    def cancelar(self, pedido) -> None:
        pedido.cambiar_a(Cancelado())


class Pagado(EstadoPedido):
    nombre = "PAGADO"

    def confirmar(self, pedido) -> None:
        raise ValueError("El pedido ya fue pagado")


class Cancelado(EstadoPedido):
    nombre = "CANCELADO"

    def confirmar(self, pedido) -> None:
        raise ValueError("El pedido está cancelado")


MAPA_ESTADOS: dict[str, type[EstadoPedido]] = {
    "BORRADOR": Borrador,
    "CONFIRMADO": Confirmado,
    "PAGADO": Pagado,
    "CANCELADO": Cancelado,
}