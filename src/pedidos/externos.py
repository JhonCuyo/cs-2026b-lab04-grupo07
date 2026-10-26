"""Servicios externos simulados para San Camilo en Línea (sin claves de API)."""


class YapeSDK:
    """SDK externo de Yape: cobra en soles (float) y retorna un dict."""

    def __init__(self, fallas: int = 0, limite: float = 500.0):
        self.fallas = fallas
        self.limite = limite
        self.llamadas = 0

    def realizar_cobro(self, telefono: str, soles: float) -> dict:
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("Timeout de red 3G al conectar con Yape API")
        if soles <= 0 or soles > self.limite:
            return {"ok": False, "operacion": None}
        return {"ok": True, "operacion": f"YAPE-{ int(soles * 100) }"}


class PlinClient:
    """Cliente externo de Plin (QA-03): cobra en céntimos (int) y retorna tupla (http_code, tx_id)."""

    def __init__(self, fallas: int = 0, limite_centimos: int = 50000):
        self.fallas = fallas
        self.limite_centimos = limite_centimos
        self.llamadas = 0

    def charge(self, amount_cents: int, phone: str) -> tuple[int, str | None]:
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("Timeout al conectar con servidor Plin")
        if amount_cents <= 0 or amount_cents > self.limite_centimos:
            return (402, None)
        return (200, f"PLIN-{amount_cents}")


class ClienteLLMFalso:
    """Doble de prueba ( Fake ) para simular respuestas del LLM al normalizar productos."""

    def __init__(self, respuesta: str = "Papa Amarilla Tumbay (Kg)"):
        self.respuesta = respuesta
        self.llamadas = 0

    def generar(self, prompt: str) -> str:
        self.llamadas += 1
        return self.respuesta