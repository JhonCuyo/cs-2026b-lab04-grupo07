"""Pruebas de contrato del servidor MCP sancamilo sin red ni LLM (mínimo 8 pruebas)."""

import asyncio
import json
import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from mcp.client import Client
from agentes.mcp.servidor_mcp import sancamilo_mcp as srv


def correr(coro_fn):
    async def _run():
        async with Client(srv.mcp) as c:
            return await coro_fn(c)
    return asyncio.run(_run())


def test_01_catalogo_estable_y_documentado():
    tools = correr(lambda c: c.list_tools()).tools
    assert [t.name for t in tools] == [
        "buscar_producto",
        "pedidos_por_puesto",
        "ejecutar_pruebas",
        "registrar_pedido_borrador",
    ]
    for t in tools:
        assert t.description and len(t.description.strip()) > 30, f"{t.name} sin descripción útil"
        assert t.input_schema["type"] == "object"


def test_02_minimo_privilegio_una_sola_herramienta_de_escritura():
    tools = correr(lambda c: c.list_tools()).tools
    escritura = [t.name for t in tools if not (t.annotations and t.annotations.read_only_hint)]
    assert escritura == ["registrar_pedido_borrador"]


def test_03_buscar_producto_oculta_agotados_e_inactivos():
    r = correr(lambda c: c.call_tool("buscar_producto", {}))
    assert not r.is_error
    datos = r.structured_content["result"]
    ids = [p["id"] for p in datos]
    assert "P-03" not in ids  # stock == 0 (ISSUE-02)
    assert "P-07" not in ids  # activo == False
    assert "P-01" in ids


def test_04_pedidos_por_puesto_devuelve_salida_estructurada():
    r = correr(lambda c: c.call_tool("pedidos_por_puesto", {"puesto": "A-01"}))
    assert not r.is_error
    assert r.structured_content is not None
    assert r.structured_content["puesto"] == "A-01"
    assert r.structured_content["cantidad_pedidos"] == 2
    assert r.structured_content["total_soles"] == "20.60"
    assert r.structured_content["comision_fija"] == 2.5


def test_05_error_de_negocio_explica_valores_validos():
    r = correr(lambda c: c.call_tool("pedidos_por_puesto", {"puesto": "A-01", "estado": "ENVIADO"}))
    assert r.is_error
    texto = r.content[0].text
    assert "Valores válidos" in texto and "PAGADO" in texto


def test_06_error_de_negocio_puesto_invalido():
    r = correr(lambda c: c.call_tool("buscar_producto", {"puesto": "Z-99"}))
    assert r.is_error
    assert "A-01" in r.content[0].text


def test_07_registrar_pedido_borrador_solo_crea_archivos_nuevos(tmp_path, monkeypatch):
    monkeypatch.setattr(srv, "RAIZ", tmp_path)
    for _ in range(2):
        r = correr(
            lambda c: c.call_tool(
                "registrar_pedido_borrador",
                {"cliente": "Cliente-Test", "puesto": "A-01", "producto": "Rocoto", "cantidad": 2},
            )
        )
        assert not r.is_error
    carpeta = tmp_path / "agentes" / "mcp" / "borradores"
    assert sorted(f.name for f in carpeta.iterdir()) == ["PEDIDO-01.json", "PEDIDO-02.json"]


def test_08_registrar_pedido_borrador_rechaza_cantidad_fuera_de_rango(tmp_path, monkeypatch):
    monkeypatch.setattr(srv, "RAIZ", tmp_path)
    r = correr(
        lambda c: c.call_tool(
            "registrar_pedido_borrador",
            {"cliente": "Cliente-Test", "puesto": "A-01", "producto": "Rocoto", "cantidad": 0},
        )
    )
    assert r.is_error
    assert "entre 1 y 50" in r.content[0].text


def test_09_recurso_adr_acepta_010_y_rechaza_path_traversal():
    ok = correr(lambda c: c.read_resource("sancamilo://adr/010"))
    assert "ADR-010" in ok.contents[0].text
    with pytest.raises(Exception):
        correr(lambda c: c.read_resource("sancamilo://adr/../../secretos"))


def test_10_prompts_disponibles_y_renderizables():
    prompts = correr(lambda c: c.list_prompts()).prompts
    nombres = [p.name for p in prompts]
    assert "oferta_del_dia" in nombres
    assert "normalizar_catalogo_producto" in nombres
    res = correr(lambda c: c.get_prompt("oferta_del_dia", {"puesto": "A-01", "productos": "Rocoto S/ 5.50"}))
    assert "<productos>" in res.messages[0].content.text
