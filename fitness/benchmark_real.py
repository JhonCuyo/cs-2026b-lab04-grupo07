"""Reto Opcional (+2 pts) — Medición real sobre un endpoint HTTP local del Catálogo Multimercado
y comparación contra el p95 de la simulación M/G/c (18 req/s concurrentes).
"""

from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
import statistics
import threading
import time
import urllib.request

# Base de datos SQLite en memoria compartida con 5000 productos de los 3 mercados e índice compuesto
_CONN = sqlite3.connect(":memory:", check_same_thread=False)
_LOCK = threading.Lock()
_CACHE_REDIS_SIM: dict[str, bytes] = {}


def inicializar_bd() -> None:
    cur = _CONN.cursor()
    cur.execute("CREATE TABLE productos (id INTEGER PRIMARY KEY, mercado_id TEXT, puesto_id INT, nombre TEXT, precio REAL)")
    cur.execute("CREATE INDEX idx_mercado_puesto ON productos (mercado_id, puesto_id)")
    filas = [
        (i, ["SAN_CAMILO", "ALTIPLANO", "RIO_SECO"][i % 3], (i % 50) + 1, f"Producto {i}", 5.0 + (i % 20))
        for i in range(1, 5001)
    ]
    cur.executemany("INSERT INTO productos VALUES (?, ?, ?, ?, ?)", filas)
    _CONN.commit()


class CatalogoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        clave = self.path
        if clave in _CACHE_REDIS_SIM:
            cuerpo = _CACHE_REDIS_SIM[clave]
        else:
            with _LOCK:
                cur = _CONN.cursor()
                cur.execute("SELECT id, nombre, precio FROM productos WHERE mercado_id='SAN_CAMILO' AND puesto_id=12")
                datos = [{"id": r[0], "nombre": r[1], "precio": r[2]} for r in cur.fetchall()]
            cuerpo = json.dumps(datos).encode("utf-8")
            _CACHE_REDIS_SIM[clave] = cuerpo

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, format, *args):
        pass  # Silenciar logs de consola durante el benchmark


def medir_endpoint_real(total_requests: int = 360, concurrencia: int = 18) -> dict:
    inicializar_bd()
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), CatalogoHandler)
    puerto = servidor.server_address[1]
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()

    latencias_ms: list[float] = []

    def hacer_request(i: int) -> float:
        # 85% de peticiones van a claves en caché, 15% fuerzan consulta indexada
        sufijo = "cached" if (i % 20) < 17 else f"miss_{i}"
        url = f"http://127.0.0.1:{puerto}/catalogo?mercado=SAN_CAMILO&puesto=12&k={sufijo}"
        t0 = time.perf_counter()
        with urllib.request.urlopen(url, timeout=5) as resp:
            resp.read()
        return (time.perf_counter() - t0) * 1000.0

    with ThreadPoolExecutor(max_workers=concurrencia) as pool:
        latencias_ms = list(pool.map(hacer_request, range(total_requests)))

    servidor.shutdown()
    latencias_ms.sort()
    p50 = latencias_ms[int(0.50 * (len(latencias_ms) - 1))]
    p95 = latencias_ms[int(0.95 * (len(latencias_ms) - 1))]
    return {"requests": total_requests, "p50_ms": round(p50, 2), "p95_ms": round(p95, 2), "media_ms": round(statistics.mean(latencias_ms), 2)}


if __name__ == "__main__":
    print("=== BENCHMARK REAL ENDPOINT CATÁLOGO (18 HILOS CONCURRENTES) ===")
    print(medir_endpoint_real())