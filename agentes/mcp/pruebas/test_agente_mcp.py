import json
import pathlib
import sys

from agentes.mcp.agente.herramientas_mcp import HerramientasMCP


RAIZ = pathlib.Path(__file__).resolve().parents[3]
SERVIDOR = RAIZ / "agentes" / "mcp" / "servidor_mcp" / "sancamilo_mcp.py"


def test_herramientas_mcp_stdio_abre_llama_y_cierra():
    with HerramientasMCP(sys.executable, [str(SERVIDOR)]) as herramientas:
        assert "pedidos_por_puesto" in herramientas.catalogo()
        respuesta = json.loads(herramientas.pedidos_por_puesto(puesto="A-01", estado="PAGADO"))

    assert respuesta["cantidad_pedidos"] == 1
    assert respuesta["total_soles"] == "11.00"
