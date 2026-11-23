"""Explora el servidor MCP sancamilo en el mismo proceso y ejecuta pruebas básicas de uso."""

import asyncio
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from mcp.client import Client
from agentes.mcp.servidor_mcp import sancamilo_mcp as srv


async def explorar():
    async with Client(srv.mcp) as c:
        tools = (await c.list_tools()).tools
        resources = (await c.list_resources()).resources
        templates = (await c.list_resource_templates()).resource_templates
        prompts = (await c.list_prompts()).prompts

        print("Servidor: sancamilo | protocolo MCP 2026-07-28")
        print("\nHERRAMIENTAS (las elige el modelo):")
        for t in tools:
            etiqueta = "solo lectura" if (t.annotations and t.annotations.read_only_hint) else "ESCRITURA"
            params = ", ".join(t.input_schema.get("properties", {}).keys())
            print(f" - {t.name}({params}) [{etiqueta}]")

        print("\nRECURSOS (los elige la aplicación):")
        for r in resources:
            print(f" - {r.uri}  {r.title}")
        for rt in templates:
            print(f" - {rt.uri_template}  {rt.title} (plantilla)")

        print("\nPROMPTS (los elige el usuario):")
        for p in prompts:
            args = ", ".join(a.name for a in (p.arguments or []))
            print(f" - {p.name}({args})")

        print("\nPRUEBAS DE USO:")
        r1 = await c.call_tool("pedidos_por_puesto", {"puesto": "A-01"})
        print(" pedidos_por_puesto(A-01) ->", r1.structured_content)
        r2 = await c.call_tool("pedidos_por_puesto", {"puesto": "Z-99"})
        print(" pedidos_por_puesto(Z-99) -> is_error =", r2.is_error, "|", r2.content[0].text[:110])
        r3 = await c.read_resource("sancamilo://adr/010")
        print(" read_resource(adr/010) ->", r3.contents[0].text.splitlines()[0])
        r4 = await c.get_prompt("oferta_del_dia", {"puesto": "A-01", "productos": "Rocoto S/ 5.50/kg"})
        print(" get_prompt(oferta_del_dia) ->", r4.messages[0].content.text[:90], "...")


if __name__ == "__main__":
    asyncio.run(explorar())
