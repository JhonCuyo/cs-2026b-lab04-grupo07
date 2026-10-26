"""Servicio de Pedidos de San Camilo en Línea (Versión final refactorizada con patrones GoF)."""

from dataclasses import dataclass
from src.pedidos.externos import YapeSDK, PlinClient, ClienteLLMFalso
from src.pedidos.estados import EstadoPedido, Borrador, MAPA_ESTADOS
from src.pedidos.pagos import (
    FabricaPasarelas,
    YapeAdapter,
    PlinAdapter,
    calcular_tarifa_envio,
)
from src.pedidos.eventos import (
    PublicadorEventos,
    NotificadorWhatsAppComerciantes,
    ActualizadorReportes,
)
from src.pedidos.ia import (
    LocalLlamaAdapter,
    ConCache,
    NormalizadorProductos,
)


@dataclass
class Linea:
    producto: str
    cantidad: int
    precio: float
    puesto: str = "Puesto General"


class Pedido:
    def __init__(
        self,
        id: int,
        celular: str,
        lineas: list[Linea] | None = None,
        modalidad: str = "RECOJO",
        estado: str = "BORRADOR",
        operacion: str | None = None,
    ):
        self.id = id
        self.celular = celular
        self.lineas = lineas if lineas is not None else []
        self.modalidad = modalidad
        self.operacion = operacion
        self._estado: EstadoPedido = MAPA_ESTADOS.get(estado, Borrador)()

    @property
    def estado(self) -> str:
        return self._estado.nombre

    def cambiar_a(self, nuevo_estado: EstadoPedido) -> None:
        self._estado = nuevo_estado

    def confirmar(self) -> None:
        self._estado.confirmar(self)

    def pagar(self, operacion: str | None) -> None:
        self._estado.pagar(self, operacion)

    def cancelar(self) -> None:
        self._estado.cancelar(self)

    def puestos_involucrados(self) -> list[str]:
        return sorted({linea.puesto for linea in self.lineas})

    def subtotal(self) -> float:
        return sum(linea.cantidad * linea.precio for linea in self.lineas)

    def total(self) -> float:
        return self.subtotal() + calcular_tarifa_envio(self.modalidad, self.subtotal())


class ServicioPedidos:
    def __init__(
        self,
        yape=None,
        plin=None,
        llm=None,
        fabrica: FabricaPasarelas | None = None,
        publicador: PublicadorEventos | None = None,
        normalizador: NormalizadorProductos | None = None,
    ):
        self.yape = yape or YapeSDK()
        self.plin = plin or PlinClient()
        self.llm = llm or ClienteLLMFalso()
        self.eventos: list[str] = []

        self.fabrica = fabrica or FabricaPasarelas()
        if not fabrica:
            self.fabrica.registrar("YAPE", lambda: YapeAdapter(self.yape))
            self.fabrica.registrar("PLIN", lambda: PlinAdapter(self.plin))

        self.publicador = publicador or PublicadorEventos()
        if not publicador:
            self.publicador.suscribir("pedido_pagado", NotificadorWhatsAppComerciantes(self.eventos))
            self.publicador.suscribir("pedido_pagado", ActualizadorReportes(self.eventos))

        proveedor_ia = ConCache(LocalLlamaAdapter(self.llm))
        self.normalizador = normalizador or NormalizadorProductos(proveedor_ia)

    def confirmar_y_pagar(self, pedido: Pedido, medio: str) -> str:
        pasarela = self.fabrica.crear(medio)
        pedido.confirmar()
        total = pedido.total()
        resultado = pasarela.cobrar(total, pedido.celular)

        if resultado.aprobado:
            pedido.pagar(resultado.operacion)
            self.publicador.publicar(
                "pedido_pagado",
                {
                    "id": pedido.id,
                    "celular": pedido.celular,
                    "total": total,
                    "puestos": pedido.puestos_involucrados(),
                },
            )
        else:
            pedido.cancelar()

        return pedido.estado

    def normalizar_producto(self, texto_crudo: str) -> str:
        return self.normalizador.normalizar(texto_crudo)