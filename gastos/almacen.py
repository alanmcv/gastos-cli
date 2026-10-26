"""Lectura y guardado de los gastos en un archivo JSON (RF-8)."""

import errno
import json
import os
from pathlib import Path

from gastos.logica import ErrorGastos, validar_gasto_guardado

# Texto del catálogo de la spec (RF-10.3).
E10 = (
    "Error: no se pudieron leer los datos guardados en {ruta} ({motivo}). "
    "No se modificaron. Revísalos o muévelos a otra carpeta para empezar de cero."
)
E11 = "Error: no se pudo guardar el gasto ({motivo}). Los datos anteriores no se modificaron."


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


def _motivo_de_escritura(error: OSError) -> str:
    if isinstance(error, PermissionError):
        return "sin permiso de escritura"
    if error.errno == errno.ENOSPC:
        return "disco lleno"
    return "error del sistema al escribir"


def guardar(ruta: Path, gastos: list) -> None:
    """Guarda la lista de gastos en UTF-8 legible, con las tildes tal cual (RF-8.1).

    Escribe primero un temporal y luego lo pone en lugar del original con
    os.replace, que es atómico: si algo falla, los datos quedan como estaban (RNF-3).
    Ante un OSError lanza ErrorGastos con E-11 (RF-8.5).
    """
    temporal = ruta.with_name(ruta.name + ".tmp")
    try:
        with open(temporal, "w", encoding="utf-8") as archivo:
            json.dump(gastos, archivo, ensure_ascii=False, indent=2)
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, ruta)
    except BaseException as error:  # también Ctrl+C: no debe quedar el temporal
        temporal.unlink(missing_ok=True)
        if isinstance(error, OSError):
            raise ErrorGastos(E11.format(motivo=_motivo_de_escritura(error)))
        raise
