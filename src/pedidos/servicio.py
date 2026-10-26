"""Servicio de Pedidos con Patrón State integrado (E3)."""

from dataclasses import dataclass, field
from src.pedidos.externos import YapeSDK, PlinClient, ClienteLLMFalso
from src.pedidos.estados import EstadoPedido, Borrador, MAPA_ESTADOS
from src.pedidos.pagos import (
    FabricaPasarelas,
    YapeAdapter,
    PlinAdapter,
    calcular_tarifa_envio,
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

    def subtotal(self) -> float:
        return sum(linea.cantidad * linea.precio for linea in self.lineas)

    def total(self) -> float:
        return self.subtotal() + calcular_tarifa_envio(self.modalidad, self.subtotal())


class ServicioPedidos:
    def __init__(self, yape=None, plin=None, llm=None, fabrica: FabricaPasarelas | None = None):
        self.yape = yape or YapeSDK()
        self.plin = plin or PlinClient()
        self.llm = llm or ClienteLLMFalso()
        self.eventos: list[str] = []
        self._cache_ia: dict[str, str] = {}

        self.fabrica = fabrica or FabricaPasarelas()
        if not fabrica:
            self.fabrica.registrar("YAPE", lambda: YapeAdapter(self.yape))
            self.fabrica.registrar("PLIN", lambda: PlinAdapter(self.plin))

    def confirmar_y_pagar(self, pedido: Pedido, medio: str) -> str:
        pasarela = self.fabrica.crear(medio)
        pedido.confirmar()
        total = pedido.total()
        resultado = pasarela.cobrar(total, pedido.celular)

        if resultado.aprobado:
            pedido.pagar(resultado.operacion)
            puestos = sorted({linea.puesto for linea in pedido.lineas})
            for puesto in puestos:
                self.eventos.append(f"whatsapp:{puesto}:Pedido {pedido.id} pagado")
            self.eventos.append(f"reporte:{pedido.id}:{total:.2f}")
        else:
            pedido.cancelar()

        return pedido.estado

    def normalizar_producto(self, texto_crudo: str) -> str:
        if not texto_crudo or not texto_crudo.strip():
            raise ValueError("El nombre del producto no puede estar vacío")
        clave = texto_crudo.strip().lower()
        if clave not in self._cache_ia:
            self._cache_ia[clave] = self.llm.generar(f"Normaliza: {clave}")
        salida = self._cache_ia[clave]
        if "s/" in salida.lower():
            raise ValueError("Guardrail: la IA incluyó un precio no permitido")
        for palabra in ("cura", "milagroso", "100% medicinal", "garantizado"):
            if palabra in salida.lower():
                raise ValueError(f"Guardrail: afirmación no permitida '{palabra}'")
        if len(salida) > 60:
            raise ValueError("Guardrail: nombre normalizado excede 60 caracteres")
        return salida