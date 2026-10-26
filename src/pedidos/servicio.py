"""Servicio de Pedidos refactorizado (evolución E2 -> E5)."""

from dataclasses import dataclass, field
from src.pedidos.externos import YapeSDK, PlinClient, ClienteLLMFalso
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


@dataclass
class Pedido:
    id: int
    celular: str
    lineas: list[Linea] = field(default_factory=list)
    modalidad: str = "RECOJO"
    estado: str = "BORRADOR"
    operacion: str | None = None

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
        if pedido.estado != "BORRADOR":
            if pedido.estado == "CANCELADO":
                raise ValueError("El pedido está cancelado")
            elif pedido.estado == "PAGADO":
                raise ValueError("El pedido ya fue pagado")
            raise ValueError("Estado no válido")

        if not pedido.lineas:
            raise ValueError("El pedido no tiene líneas")

        pasarela = self.fabrica.crear(medio)
        pedido.estado = "CONFIRMADO"

        total = pedido.total()
        resultado = pasarela.cobrar(total, pedido.celular)

        if resultado.aprobado:
            pedido.estado = "PAGADO"
            pedido.operacion = resultado.operacion
            puestos = sorted({linea.puesto for linea in pedido.lineas})
            for puesto in puestos:
                self.eventos.append(f"whatsapp:{puesto}:Pedido {pedido.id} pagado")
            self.eventos.append(f"reporte:{pedido.id}:{total:.2f}")
        else:
            pedido.estado = "CANCELADO"

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