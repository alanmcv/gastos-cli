"""Lectura y guardado de los gastos en un archivo JSON (RF-8)."""

import json
from pathlib import Path


def cargar(ruta: Path) -> list:
    """Devuelve la lista de gastos guardada; si el archivo no existe, una lista vacía (RF-8.2)."""
    try:
        texto = ruta.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    return json.loads(texto)


def guardar(ruta: Path, gastos: list) -> None:
    """Guarda la lista de gastos en UTF-8 legible, con las tildes tal cual (RF-8.1)."""
    ruta.write_text(json.dumps(gastos, ensure_ascii=False, indent=2), encoding="utf-8")
