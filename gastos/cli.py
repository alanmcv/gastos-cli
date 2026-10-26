"""Interfaz de línea de comandos de gastos-cli: lee argv, llama a la lógica y muestra resultados.

Los argumentos se interpretan a mano, sin argparse, porque argparse escribe sus
mensajes en inglés (plan, decisión D1).
"""

# Cantidad de argumentos (mínimo, máximo) de cada comando (RF-1.1).
_ARGUMENTOS = {"agregar": (2, 3), "listar": (0, 0), "resumen": (0, 0)}
_OBLIGATORIOS_DE_AGREGAR = ["el monto", "la categoría"]


class ErrorUso(Exception):
    """El usuario escribió mal el comando; termina con código 2 (RF-9.1)."""

    def __init__(self, motivo: str):
        super().__init__(motivo)
        self.motivo = motivo


def interpretar(argv: list[str]) -> tuple[str, list[str]]:
    """Devuelve (comando, args) o lanza ErrorUso con el motivo en español (RF-1.1, RF-9.1)."""
    if not argv:
        raise ErrorUso("falta el comando")
    comando, args = argv[0], argv[1:]
    if comando not in _ARGUMENTOS:
        raise ErrorUso(f'el comando "{comando}" no existe')
    minimo, maximo = _ARGUMENTOS[comando]
    if len(args) < minimo:
        # Solo agregar tiene argumentos obligatorios.
        faltan = _OBLIGATORIOS_DE_AGREGAR[len(args):]
        if len(faltan) == 1:
            raise ErrorUso(f"falta {faltan[0]}")
        raise ErrorUso("faltan " + " y ".join(faltan))
    if len(args) > maximo:
        sobran = " ".join(f'"{a}"' for a in args[maximo:])
        raise ErrorUso(f"sobran argumentos: {sobran}")
    return comando, args
