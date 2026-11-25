"""Adaptador (patrón Adapter) que conecta el núcleo ReAct del Lab 10 con un servidor MCP vía stdio."""

import asyncio
import json
import threading

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters


class HerramientasMCP:
    """Ofrece la misma interfaz que Herramientas del Lab 10 (catalogo() + métodos por herramienta)."""

    def __init__(self, command: str, args: list[str], exponer_recursos: bool = True):
        self._params = StdioServerParameters(command=command, args=args)
        self._exponer_recursos = exponer_recursos
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        self._ready = threading.Event()
        self._close_event = None
        self._session_future = None
        self._startup_error = None
        self._cliente = None
        self._tools = {}

    def _llamar(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout=60)

    def __enter__(self):
        async def _sesion():
            try:
                async with Client(self._params) as cliente:
                    self._cliente = cliente
                    lista = await cliente.list_tools()
                    self._tools = {t.name: t for t in lista.tools}
                    self._close_event = asyncio.Event()
                    self._ready.set()
                    await self._close_event.wait()
            except Exception as error:
                self._startup_error = error
                self._ready.set()
                raise

        self._session_future = asyncio.run_coroutine_threadsafe(_sesion(), self._loop)
        if not self._ready.wait(timeout=60):
            self._session_future.cancel()
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join(timeout=2)
            raise TimeoutError("El servidor MCP no completó la inicialización en 60 segundos.")
        if self._startup_error:
            try:
                self._session_future.result()
            finally:
                self._loop.call_soon_threadsafe(self._loop.stop)
                self._thread.join(timeout=2)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self._loop.call_soon_threadsafe(self._close_event.set)
            self._session_future.result(timeout=60)
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join(timeout=2)

    def catalogo(self) -> dict[str, str]:
        cat = {
            n: f"{t.description.strip()} Parámetros: {json.dumps(t.input_schema.get('properties', {}), ensure_ascii=False)}"
            for n, t in self._tools.items()
        }
        if self._exponer_recursos:
            cat["leer_recurso"] = "Lee un recurso MCP por URI (ej. sancamilo://pedidos/estados). Parámetros: uri"
        return cat

    def herramientas_de_escritura(self) -> set[str]:
        """Las anotaciones son PISTAS del servidor, no garantías: úselas solo con servidores de confianza."""
        return {n for n, t in self._tools.items() if not (t.annotations and t.annotations.read_only_hint)}

    def leer_recurso(self, uri: str) -> str:
        r = self._llamar(self._cliente.read_resource(uri))
        return "\n".join(getattr(c, "text", "") for c in r.contents)

    def __getattr__(self, nombre: str):
        if nombre.startswith("_") or nombre not in self.__dict__.get("_tools", {}):
            raise AttributeError(nombre)

        def invocar(**args):
            r = self._llamar(self._cliente.call_tool(nombre, args))
            if r.structured_content is not None:
                cuerpo = json.dumps(r.structured_content, ensure_ascii=False)
            else:
                cuerpo = " ".join(getattr(c, "text", "") for c in r.content)
            return ("ERROR: " if r.is_error else "") + cuerpo

        return invocar
