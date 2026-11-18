"""Integración del prompt versionado v3 de Normalización de Productos
detrás de la interfaz ProveedorLLM (Laboratorio 07).
"""

import json
import pathlib
from jsonschema import validate, ValidationError


class SalidaInvalidaError(Exception):
    """La respuesta del LLM no cumple el contrato JSON Schema y es descartada de forma segura."""
    pass


class GeneradorNormalizadorProductos:
    def __init__(self, proveedor_llm, version: str = "v3"):
        self._proveedor = proveedor_llm
        self.version = version
        raiz = pathlib.Path(__file__).parent.parent.parent
        self._esquema = json.loads((raiz / "asserts" / "esquema.json").read_text(encoding="utf-8"))
        self._plantilla = (raiz / "prompts" / "sancamilo_normalizar" / f"{version}.txt").read_text(encoding="utf-8")

    def normalizar(self, texto_crudo: str) -> dict:
        prompt = self._plantilla.replace("{{texto_crudo}}", texto_crudo)
        texto_respuesta = self._proveedor.completar(prompt)

        try:
            datos = json.loads(texto_respuesta)
            validate(instance=datos, schema=self._esquema)
        except (json.JSONDecodeError, ValidationError) as e:
            raise SalidaInvalidaError(f"Contrato violado en versión {self.version} para '{texto_crudo}': {e}") from e

        return datos