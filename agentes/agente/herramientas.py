"""Herramientas acotadas con sandbox sobre el repositorio de San Camilo en Línea."""

import pathlib
import subprocess
import sys


class Herramientas:
    def __init__(self, raiz: str | pathlib.Path):
        self.raiz = pathlib.Path(raiz).resolve()

    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def catalogo(self) -> dict[str, str]:
        return {
            "listar_archivos": "listar_archivos(directorio='.') -> lista rutas relativas dentro del repositorio.",
            "leer_archivo": "leer_archivo(ruta) -> devuelve el contenido UTF-8 del archivo indicado.",
            "buscar": "buscar(patron, directorio='src') -> busca texto en archivos .py y devuelve archivo:linea.",
            "editar_archivo": "editar_archivo(ruta, antes, despues) -> reemplaza un fragmento único exacto en el archivo.",
            "ejecutar_pruebas": "ejecutar_pruebas(objetivo='tests') -> ejecuta pytest sobre el objetivo dado.",
            "ver_cambios": "ver_cambios() -> devuelve git diff del repositorio.",
            "ejecutar_comando": "ejecutar_comando(comando) -> ejecuta un comando permitido por la política.",
        }

    def listar_archivos(self, directorio: str = ".") -> str:
        base = self._ruta(directorio)
        archivos = [
            str(p.relative_to(self.raiz))
            for p in sorted(base.rglob("*"))
            if p.is_file() and ".git" not in p.parts and ".venv" not in p.parts and "__pycache__" not in p.parts
        ]
        return "\n".join(archivos[:120])

    def leer_archivo(self, ruta: str) -> str:
        p = self._ruta(ruta)
        return p.read_text(encoding="utf-8")

    def buscar(self, patron: str, directorio: str = "src") -> str:
        base = self._ruta(directorio)
        hallazgos = []
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            for idx, linea in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
                if patron in linea:
                    hallazgos.append(f"{p.relative_to(self.raiz)}:{idx}: {linea.strip()}")
        return "\n".join(hallazgos) if hallazgos else "sin resultados"

    def editar_archivo(self, ruta: str, antes: str, despues: str) -> str:
        p = self._ruta(ruta)
        texto = p.read_text(encoding="utf-8")
        veces = texto.count(antes)
        if veces != 1:
            return f"ERROR: el fragmento aparece {veces} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ejecutar_pruebas(self, objetivo: str = "tests") -> str:
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", objetivo],
            cwd=self.raiz,
            capture_output=True,
            text=True,
            check=False,
        )
        salida = (res.stdout + res.stderr).strip()
        return salida[-600:] if salida else f"exit={res.returncode}"

    def ver_cambios(self) -> str:
        res = subprocess.run(
            ["git", "diff"],
            cwd=self.raiz,
            capture_output=True,
            text=True,
            check=False,
        )
        return res.stdout.strip() or "(sin cambios)"

    def ejecutar_comando(self, comando: str) -> str:
        partes = comando.split()
        if partes:
            if partes[0] == "python":
                partes[0] = sys.executable
            else:
                local_bin = pathlib.Path(sys.executable).parent / partes[0]
                if local_bin.exists():
                    partes[0] = str(local_bin)
        res = subprocess.run(
            partes,
            cwd=self.raiz,
            capture_output=True,
            text=True,
            check=False,
        )
        salida = (res.stdout + res.stderr).strip()
        return salida[-600:] if salida else f"exit={res.returncode}"
