"""Versión ingenua (ANTES del refactor) del módulo de Pedidos de San Camilo en Línea."""

from dataclasses import dataclass, field
from src.pedidos.externos import YapeSDK, PlinClient, ClienteLLMFalso


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
    modalidad: str = "RECOJO"  # RECOJO o DELIVERY
    estado: str = "BORRADOR"
    operacion: str | None = None


class ServicioPedidos:
    def __init__(self, yape=None, plin=None, llm=None):
        self.yape = yape or YapeSDK()
        self.plin = plin or PlinClient()
        self.llm = llm or ClienteLLMFalso()
        self.eventos: list[str] = []
        self._cache_ia: dict[str, str] = {}

    def confirmar_y_pagar(self, pedido: Pedido, medio: str) -> str:
        if pedido.estado != "BORRADOR":
            if pedido.estado == "CANCELADO":
                raise ValueError("El pedido está cancelado")
            elif pedido.estado == "PAGADO":
                raise ValueError("El pedido ya fue pagado")
            else:
                raise ValueError("Estado no válido")

        if not pedido.lineas:
            raise ValueError("El pedido no tiene líneas")

        if medio not in ("YAPE", "PLIN"):
            raise ValueError(f"Medio de pago no soportado: {medio}")

        subtotal = 0.0
        for linea in pedido.lineas:
            subtotal += linea.cantidad * linea.precio

        if pedido.modalidad == "DELIVERY":
            tarifa_envio = 5.00
        elif pedido.modalidad == "EXPRESS":
            tarifa_envio = 10.00
        else:
            tarifa_envio = 0.00

        total = subtotal + tarifa_envio
        pedido.estado = "CONFIRMADO"

        aprobado, operacion = False, None
        if medio == "YAPE":
            for intento in range(3):
                try:
                    r = self.yape.realizar_cobro(pedido.celular, total)
                    aprobado, operacion = r["ok"], r.get("operacion")
                    break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False
        elif medio == "PLIN":
            for intento in range(3):
                try:
                    codigo, tx = self.plin.charge(int(round(total * 100)), pedido.celular)
                    aprobado, operacion = (codigo == 200), tx
                    break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False

        if aprobado:
            pedido.estado = "PAGADO"
            pedido.operacion = operacion
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
            prompt = f"Normaliza este producto del Mercado San Camilo: {clave}"
            self._cache_ia[clave] = self.llm.generar(prompt)

        salida = self._cache_ia[clave]
        if "S/" in salida or "s/" in salida:
            raise ValueError("Guardrail: la IA incluyó un precio no permitido")

        prohibidas = ["cura", "milagroso", "100% medicinal", "garantizado"]
        for palabra in prohibidas:
            if palabra in salida.lower():
                raise ValueError(f"Guardrail: afirmación no permitida '{palabra}'")

        if len(salida) > 60:
            raise ValueError("Guardrail: nombre normalizado excede 60 caracteres")

        return salida