"""Patrón Observer: Publicación desacoplada de eventos al pagar un pedido multipuesto."""

from abc import ABC, abstractmethod


class Suscriptor(ABC):
    @abstractmethod
    def actualizar(self, evento: str, datos: dict) -> None:
        pass


class PublicadorEventos:
    def __init__(self):
        self._suscriptores: dict[str, list[Suscriptor]] = {}

    def suscribir(self, evento: str, suscriptor: Suscriptor) -> None:
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def publicar(self, evento: str, datos: dict) -> None:
        for suscriptor in self._suscriptores.get(evento, []):
            suscriptor.actualizar(evento, datos)


class NotificadorWhatsAppComerciantes(Suscriptor):
    """Suscriptor 1: Envía aviso por WhatsApp a cada puesto incluido en el pedido multipuesto."""

    def __init__(self, bandeja: list[str]):
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict) -> None:
        for puesto in datos.get("puestos", []):
            self._bandeja.append(f"whatsapp:{puesto}:Pedido {datos['id']} pagado")


class ActualizadorReportes(Suscriptor):
    """Suscriptor 2: Registra el monto total del pedido pagado para el módulo de Reportes."""

    def __init__(self, bandeja: list[str]):
        self._bandeja = bandeja

    def actualizar(self, evento: str, datos: dict) -> None:
        self._bandeja.append(f"reporte:{datos['id']}:{datos['total']:.2f}")