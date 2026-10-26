"""Patrones Strategy, Adapter, Decorator y Factory para Pagos y Tarifas de San Camilo."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoPago:
    aprobado: bool
    operacion: str | None = None


class PasarelaPago(ABC):
    """Puerto (Strategy): interfaz común para cualquier medio de pago."""

    @abstractmethod
    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        pass


class YapeAdapter(PasarelaPago):
    """Adapter: adapta YapeSDK (celular, soles -> dict) al puerto PasarelaPago."""

    def __init__(self, sdk):
        self._sdk = sdk

    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        r = self._sdk.realizar_cobro(celular, monto)
        return ResultadoPago(aprobado=bool(r["ok"]), operacion=r.get("operacion"))


class PlinAdapter(PasarelaPago):
    """Adapter: adapta PlinClient (centimos, celular -> tupla HTTP) al puerto PasarelaPago."""

    def __init__(self, cliente):
        self._cliente = cliente

    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        centimos = int(round(monto * 100))
        codigo, tx = self._cliente.charge(centimos, celular)
        return ResultadoPago(aprobado=(codigo == 200), operacion=tx)


class ConReintentos(PasarelaPago):
    """Decorator: envuelve una PasarelaPago y reintenta solo ante TimeoutError (red 3G)."""

    def __init__(self, interna: PasarelaPago, intentos: int = 3):
        self._interna = interna
        self._intentos = intentos

    def cobrar(self, monto: float, celular: str) -> ResultadoPago:
        for _ in range(self._intentos):
            try:
                return self._interna.cobrar(monto, celular)
            except TimeoutError:
                continue
        return ResultadoPago(aprobado=False, operacion=None)


class FabricaPasarelas:
    """Factory (registro): instancia la estrategia de pago sin usar if/elif."""

    def __init__(self):
        self._creadores: dict[str, callable] = {}

    def registrar(self, medio: str, creador: callable) -> None:
        self._creadores[medio.upper()] = creador

    def crear(self, medio: str) -> PasarelaPago:
        clave = medio.upper()
        if clave not in self._creadores:
            raise ValueError(f"Medio de pago no soportado: {medio}")
        return ConReintentos(self._creadores[clave]())


# Strategy para cálculo de tarifa de entrega (Tabla 7 - Caso 7: San Camilo en Línea)
TARIFAS_MODALIDAD: dict[str, callable] = {
    "RECOJO": lambda _subtotal: 0.00,
    "DELIVERY": lambda _subtotal: 5.00,
    "EXPRESS": lambda _subtotal: 10.00,
}


def calcular_tarifa_envio(modalidad: str, subtotal: float) -> float:
    estrategia = TARIFAS_MODALIDAD.get(modalidad.upper(), TARIFAS_MODALIDAD["RECOJO"])
    return estrategia(subtotal)