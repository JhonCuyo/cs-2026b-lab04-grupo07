"""Espía transparente de stdio: reenvía líneas JSON-RPC y las registra en un archivo JSONL."""

import json
import pathlib
import subprocess
import sys
import threading
import time


def main():
    if len(sys.argv) < 3:
        print("Uso: python espia.py <archivo_traza.jsonl> <comando_servidor...>", file=sys.stderr)
        sys.exit(1)

    traza = pathlib.Path(sys.argv[1])
    traza.parent.mkdir(parents=True, exist_ok=True)
    cmd = sys.argv[2:]
    lock = threading.Lock()
    t0 = time.perf_counter()

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr, bufsize=0)

    def registrar(direccion: str, linea: bytes):
        texto = linea.decode("utf-8", errors="replace").strip()
        if not texto:
            return
        try:
            payload = json.loads(texto)
        except json.JSONDecodeError:
            payload = {"raw": texto}
        evento = {
            "t_ms": round((time.perf_counter() - t0) * 1000, 2),
            "dir": direccion,
            "bytes": len(linea),
            "msg": payload,
        }
        with lock:
            with open(traza, "a", encoding="utf-8") as f:
                f.write(json.dumps(evento, ensure_ascii=False) + "\n")

    def reenviar(origen, destino, direccion: str):
        for linea in iter(origen.readline, b""):
            registrar(direccion, linea)
            destino.write(linea)
            destino.flush()
        try:
            destino.close()
        except Exception:
            pass

    h1 = threading.Thread(target=reenviar, args=(sys.stdin.buffer, proc.stdin, "host->servidor"), daemon=True)
    h2 = threading.Thread(target=reenviar, args=(proc.stdout, sys.stdout.buffer, "servidor->host"), daemon=True)
    h1.start()
    h2.start()
    proc.wait()
    h2.join(timeout=2)


if __name__ == "__main__":
    main()
