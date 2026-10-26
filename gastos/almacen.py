"""Lectura y guardado de los gastos en un archivo JSON (RF-8)."""

import json
from pathlib import Path

from gastos.logica import ErrorGastos, validar_gasto_guardado

# Texto del catálogo de la spec (RF-10.3).
E10 = (
    "Error: no se pudieron leer los datos guardados en {ruta} ({motivo}). "
    "No se modificaron. Revísalos o muévelos a otra carpeta para empezar de cero."
)


def _no_se_pudo_leer(ruta: Path, motivo: str) -> ErrorGastos:
    return ErrorGastos(E10.format(ruta=ruta, motivo=motivo))


def cargar(ruta: Path) -> list:
    """Devuelve la lista de gastos guardada; si el archivo no existe, una lista vacía (RF-8.2).

    Si los datos existen pero no se pueden leer, lanza ErrorGastos con E-10 y no
    modifica nada (RF-8.3).
    """
    try:
        texto = ruta.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except PermissionError:
        raise _no_se_pudo_leer(ruta, "sin permiso de lectura")
    except UnicodeDecodeError:
        raise _no_se_pudo_leer(ruta, "el contenido no es JSON válido")
    except OSError:
        raise _no_se_pudo_leer(ruta, "error del sistema al leer")

    if texto.strip() == "":
        raise _no_se_pudo_leer(ruta, "el archivo está vacío")
    try:
        gastos = json.loads(texto)
    except json.JSONDecodeError:
        raise _no_se_pudo_leer(ruta, "el contenido no es JSON válido")
    if not isinstance(gastos, list):
        raise _no_se_pudo_leer(ruta, "el contenido no es una lista de gastos")
    for numero, gasto in enumerate(gastos, start=1):
        if not validar_gasto_guardado(gasto):
            raise _no_se_pudo_leer(ruta, f"el gasto número {numero} no es válido")
    return gastos


def guardar(ruta: Path, gastos: list) -> None:
    """Guarda la lista de gastos en UTF-8 legible, con las tildes tal cual (RF-8.1)."""
    ruta.write_text(json.dumps(gastos, ensure_ascii=False, indent=2), encoding="utf-8")
