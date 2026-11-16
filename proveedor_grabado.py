"""Proveedor personalizado para promptfoo que lee respuestas grabadas (fixtures)."""

import pathlib
import json


def call_api(prompt, options, context):
    vars_data = context.get("vars", {})
    # Identificar qué caso de prueba se está ejecutando según la variable texto_crudo
    texto = vars_data.get("texto_crudo", "").strip().lower()

    # Mapeo de casos grabados para la versión v1
    version = "v1"
    if "papa amarilla tumbay" in texto:
        caso_id = "caso_1"
    elif "papa amarila" in texto:
        caso_id = "caso_2"
    elif "queso paria" in texto:
        caso_id = "caso_3"
    elif "leche fresca" in texto:
        caso_id = "caso_4"
    elif "rocoto relleno" in texto:
        caso_id = "caso_5"
    elif "xyzqwerty" in texto:
        caso_id = "caso_6"
    elif texto == "":
        caso_id = "caso_7"
    elif "ignora" in texto:
        caso_id = "caso_8"
    else:
        caso_id = "caso_1"

    ruta = pathlib.Path(__file__).parent / "grabaciones" / version / f"{caso_id}.txt"
    if ruta.exists():
        output_text = ruta.read_text(encoding="utf-8")
    else:
        output_text = json.dumps({
            "entrada_original": texto,
            "encontrado": False,
            "nombre_normalizado": texto,
            "categoria": "Desconocido",
            "confianza": 0.1
        })

    return {
        "output": output_text
    }