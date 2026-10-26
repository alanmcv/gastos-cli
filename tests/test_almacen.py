import errno
import json
import os
from pathlib import Path

import pytest

from gastos.almacen import cargar, guardar
from gastos.logica import ErrorGastos


def e10(ruta, motivo):
    return (
        f"Error: no se pudieron leer los datos guardados en {ruta} ({motivo}). "
        "No se modificaron. Revísalos o muévelos a otra carpeta para empezar de cero."
    )


GASTOS = [
    {"fecha": "2026-10-03", "monto_centavos": 2550, "categoria": "café", "descripcion": "almuerzo ☕"},
    {"fecha": "2026-10-04", "monto_centavos": 300, "categoria": "transporte", "descripcion": "", "nota": "extra"},
]


def test_cargar_sin_datos_guardados_devuelve_lista_vacia(tmp_path):
    """RF-8.2: si todavía no hay datos guardados, se trabaja como si no hubiera gastos."""
    assert cargar(tmp_path / "gastos.json") == []


def test_guardar_y_cargar_ida_y_vuelta(tmp_path):
    """RF-8.1, RF-8.4: lo guardado se recupera igual, incluidas las claves de más."""
    ruta = tmp_path / "gastos.json"
    guardar(ruta, GASTOS)
    assert cargar(ruta) == GASTOS


def test_guardar_escribe_utf8_legible(tmp_path):
    """RF-8.1: el JSON se guarda en UTF-8 con las tildes y emojis tal cual (sin \\u00e9)."""
    ruta = tmp_path / "gastos.json"
    guardar(ruta, GASTOS)
    texto = ruta.read_text(encoding="utf-8")
    assert "café" in texto and "☕" in texto
    assert "\\u" not in texto


GASTO_INVALIDO = {"fecha": "2026-10-04", "monto_centavos": 0, "categoria": "comida", "descripcion": ""}


@pytest.mark.parametrize(
    "contenido, motivo",
    [
        (b"", "el archivo está vacío"),
        (b"  \n", "el archivo está vacío"),
        (b"[{roto", "el contenido no es JSON válido"),
        (b"\xff\xfe\x00basura", "el contenido no es JSON válido"),
        (b'{"gastos": []}', "el contenido no es una lista de gastos"),
        (
            json.dumps([GASTOS[0], GASTO_INVALIDO]).encode("utf-8"),
            "el gasto número 2 no es válido",
        ),
    ],
)
def test_cargar_datos_ilegibles_da_e10_sin_modificarlos(tmp_path, contenido, motivo):
    """RF-8.3, RF-10.3: datos vacíos, rotos, que no son lista o con un gasto inválido dan E-10 y no se tocan."""
    ruta = tmp_path / "gastos.json"
    ruta.write_bytes(contenido)
    with pytest.raises(ErrorGastos) as error:
        cargar(ruta)
    assert str(error.value) == e10(ruta, motivo)
    assert ruta.read_bytes() == contenido


@pytest.mark.parametrize(
    "excepcion, motivo",
    [
        (PermissionError("acceso denegado"), "sin permiso de lectura"),
        (OSError("fallo del disco"), "error del sistema al leer"),
    ],
)
def test_cargar_sin_poder_leer_da_e10(tmp_path, monkeypatch, excepcion, motivo):
    """RF-8.3, RF-10.3: sin permiso de lectura (simulado; chmod no es fiable en Windows) da E-10."""
    ruta = tmp_path / "gastos.json"
    guardar(ruta, GASTOS)
    antes = ruta.read_bytes()

    def leer_con_error(self, *args, **kwargs):
        raise excepcion

    monkeypatch.setattr(Path, "read_text", leer_con_error)
    with pytest.raises(ErrorGastos) as error:
        cargar(ruta)
    monkeypatch.undo()
    assert str(error.value) == e10(ruta, motivo)
    assert ruta.read_bytes() == antes


def e11(motivo):
    return f"Error: no se pudo guardar el gasto ({motivo}). Los datos anteriores no se modificaron."


def reemplazo_que_falla(excepcion):
    def reemplazar(origen, destino):
        raise excepcion

    return reemplazar


@pytest.mark.parametrize(
    "excepcion, motivo",
    [
        (PermissionError(errno.EACCES, "acceso denegado"), "sin permiso de escritura"),
        (OSError(errno.ENOSPC, "no queda espacio"), "disco lleno"),
        (OSError(errno.EIO, "fallo de E/S"), "error del sistema al escribir"),
    ],
)
def test_guardar_con_error_da_e11_y_deja_los_datos_intactos(tmp_path, monkeypatch, excepcion, motivo):
    """RF-8.5, RNF-3, RF-10.3: si falla el guardado, E-11, el original intacto y sin temporal."""
    ruta = tmp_path / "gastos.json"
    guardar(ruta, GASTOS[:1])
    antes = ruta.read_bytes()
    monkeypatch.setattr(os, "replace", reemplazo_que_falla(excepcion))
    with pytest.raises(ErrorGastos) as error:
        guardar(ruta, GASTOS)
    assert str(error.value) == e11(motivo)
    assert ruta.read_bytes() == antes
    assert list(tmp_path.iterdir()) == [ruta]


def test_guardar_interrumpido_con_ctrl_c_deja_los_datos_intactos(tmp_path, monkeypatch):
    """RNF-3: un Ctrl+C mientras se guarda no deja datos a medio escribir ni el temporal."""
    ruta = tmp_path / "gastos.json"
    guardar(ruta, GASTOS[:1])
    antes = ruta.read_bytes()
    monkeypatch.setattr(os, "replace", reemplazo_que_falla(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        guardar(ruta, GASTOS)
    assert ruta.read_bytes() == antes
    assert list(tmp_path.iterdir()) == [ruta]


def test_guardar_reemplaza_un_archivo_existente(tmp_path):
    """RF-8.1: guardar de nuevo reemplaza el contenido anterior."""
    ruta = tmp_path / "gastos.json"
    guardar(ruta, GASTOS[:1])
    guardar(ruta, GASTOS)
    assert cargar(ruta) == GASTOS
    assert list(tmp_path.iterdir()) == [ruta]
