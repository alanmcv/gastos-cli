"""Lógica de gastos-cli: funciones puras, sin print, input ni archivos."""

import re

# Textos del catálogo de la spec (RF-10.3).
E1 = "Error: falta el monto. Ejemplo: gastos agregar 25.50 comida"
E2 = "Error: el monto debe ser mayor que cero."
E3 = "Error: el monto puede tener como máximo 2 decimales."
E4 = (
    'Error: "{valor}" no es un monto válido. Usa solo cifras y, si quieres, '
    "un punto o una coma con hasta 2 decimales (ej.: 25.50)."
)
E5 = "Error: el monto máximo por gasto es Bs 1000000.00."

MONTO_MAXIMO_CENTAVOS = 100_000_000

# Cifras ASCII y, opcionalmente, un separador (punto o coma) con 1 o 2 decimales (RF-3.2).
_MONTO_VALIDO = re.compile(r"([0-9]+)(?:[.,]([0-9]{1,2}))?")
_DEMASIADOS_DECIMALES = re.compile(r"[0-9]+[.,][0-9]{3,}")


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


def formatear_monto(centavos: int) -> str:
    """Convierte centavos en texto para el usuario: 2550 -> "Bs 25.50" (RF-10.1)."""
    return f"Bs {centavos // 100}.{centavos % 100:02d}"


def formatear_fecha(iso: str) -> str:
    """Convierte una fecha "AAAA-MM-DD" en "DD/MM/AAAA" (RF-10.2)."""
    anio, mes, dia = iso.split("-")
    return f"{dia}/{mes}/{anio}"
