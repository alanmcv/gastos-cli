"""Lógica de gastos-cli: funciones puras, sin print, input ni archivos."""

import re

# Cifras ASCII y, opcionalmente, un separador (punto o coma) con 1 o 2 decimales (RF-3.2).
_MONTO_VALIDO = re.compile(r"([0-9]+)(?:[.,]([0-9]{1,2}))?")


def parsear_monto(texto: str) -> int:
    """Convierte el texto de un monto en centavos: "25,5" -> 2550 (RF-3)."""
    coincidencia = _MONTO_VALIDO.fullmatch(texto.strip())
    entero, decimales = coincidencia.groups()
    return int(entero) * 100 + int((decimales or "0").ljust(2, "0"))


def formatear_monto(centavos: int) -> str:
    """Convierte centavos en texto para el usuario: 2550 -> "Bs 25.50" (RF-10.1)."""
    return f"Bs {centavos // 100}.{centavos % 100:02d}"


def formatear_fecha(iso: str) -> str:
    """Convierte una fecha "AAAA-MM-DD" en "DD/MM/AAAA" (RF-10.2)."""
    anio, mes, dia = iso.split("-")
    return f"{dia}/{mes}/{anio}"
