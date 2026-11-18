"""Pruebas unitarias para el generador de normalización basado en prompts (Lab 09)."""

import pytest
from src.pedidos.generador_normalizador import GeneradorNormalizadorProductos, SalidaInvalidaError


class ProveedorFalsoValido:
    def completar(self, prompt: str) -> str:
        return '{"entrada_original": "papa", "encontrado": true, "nombre_normalizado": "Papa Blanca (Kg)", "categoria": "Verduras y Tubérculos", "confianza": 0.98}'


class ProveedorFalsoInvalido:
    def completar(self, prompt: str) -> str:
        return '{"entrada_original": "papa", "encontrado": "NO_BOOLEANO", "categoria": "INVALIDA"}'


def test_generador_acepta_salida_valida_por_esquema():
    gen = GeneradorNormalizadorProductos(ProveedorFalsoValido(), version="v3")
    res = gen.normalizar("papa")
    assert res["encontrado"] is True
    assert res["categoria"] == "Verduras y Tubérculos"


def test_generador_rechaza_salida_invalida_por_esquema():
    gen = GeneradorNormalizadorProductos(ProveedorFalsoInvalido(), version="v3")
    with pytest.raises(SalidaInvalidaError, match="Contrato violado"):
        gen.normalizar("papa")