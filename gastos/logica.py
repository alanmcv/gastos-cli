"""Lógica de gastos-cli: funciones puras, sin print, input ni archivos."""

import re
import unicodedata
from datetime import date

# Textos del catálogo de la spec (RF-10.3).
E1 = "Error: falta el monto. Ejemplo: gastos agregar 25.50 comida"
E2 = "Error: el monto debe ser mayor que cero."
E3 = "Error: el monto puede tener como máximo 2 decimales."
E4 = (
    'Error: "{valor}" no es un monto válido. Usa solo cifras y, si quieres, '
    "un punto o una coma con hasta 2 decimales (ej.: 25.50)."
)
E5 = "Error: el monto máximo por gasto es Bs 1000000.00."
E6 = "Error: falta la categoría."
E7 = (
    'Error: la categoría solo puede tener letras, cifras, espacios, "-" y "_", '
    "y debe empezar con una letra o una cifra."
)
E8 = "Error: la categoría puede tener como máximo 30 caracteres."
E9 = "Error: la descripción puede tener como máximo 100 caracteres."
E13 = "Error: la descripción tiene caracteres no permitidos."

MONTO_MAXIMO_CENTAVOS = 100_000_000
CATEGORIA_MAXIMO_CARACTERES = 30
DESCRIPCION_MAXIMO_CARACTERES = 100

# Cifras ASCII y, opcionalmente, un separador (punto o coma) con 1 o 2 decimales (RF-3.2).
_MONTO_VALIDO = re.compile(r"([0-9]+)(?:[.,]([0-9]{1,2}))?")
_DEMASIADOS_DECIMALES = re.compile(r"[0-9]+[.,][0-9]{3,}")
_FECHA_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_CLAVES_DE_GASTO = {"fecha", "monto_centavos", "categoria", "descripcion"}


class ErrorGastos(Exception):
    """Error que se muestra al usuario; su texto es uno del catálogo de la spec."""


def parsear_monto(texto: str) -> int:
    """Convierte el texto de un monto en centavos: "25,5" -> 2550 (RF-3).

    Si el monto no es válido, lanza ErrorGastos con el primer error de RF-3.5.
    """
    texto = texto.strip()
    if texto == "":
        raise ErrorGastos(E1)
    if texto.startswith("-"):
        raise ErrorGastos(E2)
    if _DEMASIADOS_DECIMALES.fullmatch(texto):
        raise ErrorGastos(E3)
    coincidencia = _MONTO_VALIDO.fullmatch(texto)
    if coincidencia is None:
        raise ErrorGastos(E4.format(valor=texto))
    entero, decimales = coincidencia.groups()
    centavos = int(entero) * 100 + int((decimales or "0").ljust(2, "0"))
    if centavos == 0:
        raise ErrorGastos(E2)
    if centavos > MONTO_MAXIMO_CENTAVOS:
        raise ErrorGastos(E5)
    return centavos


def _normalizar_espacios(texto: str) -> str:
    """Aplica NFC, quita los espacios en blanco de los extremos y colapsa los internos (RF-4.1, RF-5.1).

    NFC hace que una "é" escrita como "e" + tilde combinante cuente como 1 carácter.
    """
    return " ".join(unicodedata.normalize("NFC", texto).split())


def _es_letra_o_cifra(caracter: str) -> bool:
    """Letras de cualquier alfabeto (con tilde, ñ, ü) o cifras 0-9; "²" no cuenta como cifra."""
    return caracter.isalpha() or caracter in "0123456789"


def normalizar_categoria(texto: str) -> str:
    """Normaliza una categoría: "  Comida  Rápida " -> "comida rápida" (RF-4.1).

    Si la categoría no es válida, lanza ErrorGastos con E-6, E-7 o E-8 (RF-4.3 a RF-4.5).
    """
    categoria = _normalizar_espacios(texto).lower()
    if categoria == "":
        raise ErrorGastos(E6)
    if not _es_letra_o_cifra(categoria[0]) or not all(
        _es_letra_o_cifra(c) or c in " -_" for c in categoria
    ):
        raise ErrorGastos(E7)
    if len(categoria) > CATEGORIA_MAXIMO_CARACTERES:
        raise ErrorGastos(E8)
    return categoria


def normalizar_descripcion(texto: str) -> str:
    """Normaliza una descripción como la categoría, pero sin pasarla a minúsculas (RF-5.1, RF-5.2).

    Si no es válida, lanza ErrorGastos con E-13 o E-9, en ese orden (RF-5.4, RF-5.5).
    """
    descripcion = _normalizar_espacios(texto)
    # ponytail: isprintable() rechaza el carácter de unión de los emojis compuestos
    # (por ejemplo 👨‍👩‍👧); la spec solo pide emojis simples. Habría que permitir U+200D si hace falta.
    if not descripcion.isprintable():
        raise ErrorGastos(E13)
    if len(descripcion) > DESCRIPCION_MAXIMO_CARACTERES:
        raise ErrorGastos(E9)
    return descripcion


def crear_gasto(monto: str, categoria: str, descripcion: str, hoy: date) -> dict:
    """Valida los datos y arma un gasto con la fecha de hoy (RF-2.1, RF-2.3).

    Valida el monto, luego la categoría y luego la descripción; el primer error
    detiene todo (RF-2.4).
    """
    monto_centavos = parsear_monto(monto)
    categoria = normalizar_categoria(categoria)
    descripcion = normalizar_descripcion(descripcion)
    return {
        "fecha": hoy.isoformat(),
        "monto_centavos": monto_centavos,
        "categoria": categoria,
        "descripcion": descripcion,
    }


def _es_fecha_iso(valor) -> bool:
    """Exactamente "AAAA-MM-DD" y una fecha real; fromisoformat solo no basta porque acepta "20261026"."""
    if not isinstance(valor, str) or not _FECHA_ISO.fullmatch(valor):
        return False
    try:
        date.fromisoformat(valor)
    except ValueError:
        return False
    return True


def validar_gasto_guardado(gasto) -> bool:
    """Indica si un gasto leído de los datos guardados cumple las reglas de la spec (RF-8.3).

    Las claves de más se ignoran (RF-8.4).
    """
    if not isinstance(gasto, dict) or not _CLAVES_DE_GASTO <= gasto.keys():
        return False
    monto = gasto["monto_centavos"]
    categoria = gasto["categoria"]
    descripcion = gasto["descripcion"]
    # type() y no isinstance(), porque True también es un int.
    if type(monto) is not int or not 1 <= monto <= MONTO_MAXIMO_CENTAVOS:
        return False
    if not _es_fecha_iso(gasto["fecha"]):
        return False
    if not isinstance(categoria, str) or not isinstance(descripcion, str):
        return False
    try:
        return (
            normalizar_categoria(categoria) == categoria
            and normalizar_descripcion(descripcion) == descripcion
        )
    except ErrorGastos:
        return False


def gastos_del_mes(gastos: list, anio: int, mes: int) -> list:
    """Devuelve los gastos de ese mes y año, en el orden en que se registraron (RF-6.1, RF-6.4)."""
    prefijo = f"{anio:04d}-{mes:02d}-"
    return [g for g in gastos if g["fecha"].startswith(prefijo)]


def formatear_monto(centavos: int) -> str:
    """Convierte centavos en texto para el usuario: 2550 -> "Bs 25.50" (RF-10.1)."""
    return f"Bs {centavos // 100}.{centavos % 100:02d}"


def formatear_fecha(iso: str) -> str:
    """Convierte una fecha "AAAA-MM-DD" en "DD/MM/AAAA" (RF-10.2)."""
    anio, mes, dia = iso.split("-")
    return f"{dia}/{mes}/{anio}"
