"""Lógica de gastos-cli: funciones puras, sin print, input ni archivos."""


def formatear_monto(centavos: int) -> str:
    """Convierte centavos en texto para el usuario: 2550 -> "Bs 25.50" (RF-10.1)."""
    return f"Bs {centavos // 100}.{centavos % 100:02d}"


def formatear_fecha(iso: str) -> str:
    """Convierte una fecha "AAAA-MM-DD" en "DD/MM/AAAA" (RF-10.2)."""
    anio, mes, dia = iso.split("-")
    return f"{dia}/{mes}/{anio}"
