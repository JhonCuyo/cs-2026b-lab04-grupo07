"""Componente de IA aislado: Normalizador de productos de San Camilo en Línea."""

from abc import ABC, abstractmethod


class ProveedorLLM(ABC):
    """Puerto Strategy: interfaz común para cualquier proveedor de modelo de lenguaje."""

    @abstractmethod
    def completar(self, prompt: str) -> str:
        pass


class LocalLlamaAdapter(ProveedorLLM):
    """Adapter: adapta un cliente LLM (simulado o local) a la interfaz ProveedorLLM."""

    def __init__(self, cliente):
        self._cliente = cliente

    def completar(self, prompt: str) -> str:
        return self._cliente.generar(prompt)


class ConCache(ProveedorLLM):
    """Decorator: almacena en caché respuestas para evitar llamadas y costos repetidos al LLM."""

    def __init__(self, interno: ProveedorLLM):
        self._interno = interno
        self._cache: dict[str, str] = {}

    def completar(self, prompt: str) -> str:
        if prompt not in self._cache:
            self._cache[prompt] = self._interno.completar(prompt)
        return self._cache[prompt]


class Guardrail(ABC):
    """Handler base (Chain of Responsibility): valida la salida no determinista del LLM."""

    def __init__(self, siguiente: "Guardrail | None" = None):
        self._siguiente = siguiente

    def validar(self, texto: str) -> str:
        texto_limpio = self._aplicar(texto)
        return self._siguiente.validar(texto_limpio) if self._siguiente else texto_limpio

    @abstractmethod
    def _aplicar(self, texto: str) -> str:
        pass


class SinPreciosInfiltrados(Guardrail):
    """Eslabón 1: impide que el LLM invente o incruste precios en el nombre del producto."""

    def _aplicar(self, texto: str) -> str:
        if "s/" in texto.lower() or "soles" in texto.lower():
            raise ValueError("Guardrail: la IA incluyó un precio no permitido")
        return texto


class SinAfirmacionesMedicas(Guardrail):
    """Eslabón 2: bloquea promesas engañosas o médicas en alimentos del mercado."""

    PROHIBIDAS = ("cura", "milagroso", "100% medicinal", "garantizado")

    def _aplicar(self, texto: str) -> str:
        texto_min = texto.lower()
        for palabra in self.PROHIBIDAS:
            if palabra in texto_min:
                raise ValueError(f"Guardrail: afirmación no permitida '{palabra}'")
        return texto


class LongitudMaximaCatalogo(Guardrail):
    """Eslabón 3: asegura nombres concisos para pantallas pequeñas de gama baja (QA-01)."""

    def __init__(self, max_chars: int = 60, siguiente: Guardrail | None = None):
        super().__init__(siguiente)
        self.max_chars = max_chars

    def _aplicar(self, texto: str) -> str:
        texto_limpio = texto.strip()
        if len(texto_limpio) > self.max_chars:
            raise ValueError(f"Guardrail: nombre normalizado excede {self.max_chars} caracteres")
        return texto_limpio


def construir_cadena_guardrails() -> Guardrail:
    return SinPreciosInfiltrados(
        SinAfirmacionesMedicas(
            LongitudMaximaCatalogo(max_chars=60)
        )
    )


class NormalizadorProductos:
    """Servicio de dominio que coordina el ProveedorLLM decorado y la cadena de Guardrails."""

    def __init__(self, proveedor: ProveedorLLM, guardrail: Guardrail | None = None):
        self._proveedor = proveedor
        self._guardrail = guardrail or construir_cadena_guardrails()

    def normalizar(self, texto_crudo: str) -> str:
        if not texto_crudo or not texto_crudo.strip():
            raise ValueError("El nombre del producto no puede estar vacío")
        clave = texto_crudo.strip().lower()
        prompt = f"Normaliza este producto del Mercado San Camilo: {clave}"
        respuesta = self._proveedor.completar(prompt)
        return self._guardrail.validar(respuesta)