"""Interfaz de línea de comandos de gastos-cli: lee argv, llama a la lógica y muestra resultados.

Los argumentos se interpretan a mano, sin argparse, porque argparse escribe sus
mensajes en inglés (plan, decisión D1).
"""

# Cantidad de argumentos (mínimo, máximo) de cada comando (RF-1.1).
_ARGUMENTOS = {"agregar": (2, 3), "listar": (0, 0), "resumen": (0, 0)}
_OBLIGATORIOS_DE_AGREGAR = ["el monto", "la categoría"]

_EJEMPLO_AGREGAR = 'gastos agregar 25.50 comida "almuerzo en la U"'
# (uso, descripción) de cada línea de la ayuda general (RF-1.2).
_LINEAS_DE_AYUDA = [
    ("gastos agregar <monto> <categoria> [descripcion]", "Registra un gasto con la fecha de hoy"),
    ("gastos listar", "Muestra los gastos de este mes"),
    ("gastos resumen", "Muestra el total por categoría de este mes"),
    ("gastos --ayuda", "Muestra esta ayuda"),
]
_AYUDA_GENERAL = "\n".join(
    ["Uso:"]
    + [f"  {uso:<48}   {descripcion}" for uso, descripcion in _LINEAS_DE_AYUDA]
    + [f"Ejemplo: {_EJEMPLO_AGREGAR}"]
)
_AYUDA_DE_COMANDO = {
    "agregar": f"Uso: gastos agregar <monto> <categoria> [descripcion]\nEjemplo: {_EJEMPLO_AGREGAR}",
    "listar": "Uso: gastos listar\nEjemplo: gastos listar",
    "resumen": "Uso: gastos resumen\nEjemplo: gastos resumen",
}


def texto_ayuda(comando: str | None = None) -> str:
    """Ayuda de un comando, o la general si no se indica uno (RF-1.2)."""
    return _AYUDA_DE_COMANDO.get(comando, _AYUDA_GENERAL)


class ErrorUso(Exception):
    """El usuario escribió mal el comando; termina con código 2 (RF-9.1).

    Su texto es E-12: "Error: <motivo>." seguido de la ayuda del comando, o de la general.
    """

    def __init__(self, motivo: str, comando: str | None = None):
        super().__init__(f"Error: {motivo}.\n{texto_ayuda(comando)}")
        self.motivo = motivo


def _es_opcion(argumento: str) -> bool:
    """Empieza con "-" y no sigue con una cifra: "-ahorro" es una opción, "-5" es un valor (RF-1.3)."""
    return argumento.startswith("-") and not (len(argumento) > 1 and argumento[1] in "0123456789")


def interpretar(argv: list[str]) -> tuple[str, list[str]]:
    """Devuelve (comando, args) o lanza ErrorUso con el motivo en español (RF-1.1, RF-1.3, RF-9.1).

    Si aparece --ayuda devuelve ("ayuda", [comando]), o ("ayuda", []) para la ayuda general (RF-1.2).
    """
    if not argv:
        raise ErrorUso("falta el comando")
    comando, args = argv[0], argv[1:]
    if "--ayuda" in argv:
        return "ayuda", [comando] if comando in _ARGUMENTOS else []
    if comando not in _ARGUMENTOS:
        raise ErrorUso(f'el comando "{comando}" no existe')
    for argumento in args:
        if _es_opcion(argumento):
            raise ErrorUso(f'la opción "{argumento}" no existe', comando)
    minimo, maximo = _ARGUMENTOS[comando]
    if len(args) < minimo:
        # Solo agregar tiene argumentos obligatorios.
        faltan = _OBLIGATORIOS_DE_AGREGAR[len(args):]
        if len(faltan) == 1:
            raise ErrorUso(f"falta {faltan[0]}", comando)
        raise ErrorUso("faltan " + " y ".join(faltan), comando)
    if len(args) > maximo:
        sobran = " ".join(f'"{a}"' for a in args[maximo:])
        raise ErrorUso(f"sobran argumentos: {sobran}", comando)
    return comando, args
