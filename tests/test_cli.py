import pytest

from gastos.cli import ErrorUso, interpretar, texto_ayuda

AYUDA_GENERAL = "\n".join(
    [
        "Uso:",
        "  gastos agregar <monto> <categoria> [descripcion]   Registra un gasto con la fecha de hoy",
        "  gastos listar" + " " * 38 + "Muestra los gastos de este mes",
        "  gastos resumen" + " " * 37 + "Muestra el total por categoría de este mes",
        "  gastos --ayuda" + " " * 37 + "Muestra esta ayuda",
        'Ejemplo: gastos agregar 25.50 comida "almuerzo en la U"',
    ]
)
AYUDA_AGREGAR = (
    "Uso: gastos agregar <monto> <categoria> [descripcion]\n"
    'Ejemplo: gastos agregar 25.50 comida "almuerzo en la U"'
)


@pytest.mark.parametrize(
    "argv, comando, args",
    [
        (["agregar", "25", "comida"], "agregar", ["25", "comida"]),
        (["agregar", "25", "comida", "almuerzo en la U"], "agregar", ["25", "comida", "almuerzo en la U"]),
        (["listar"], "listar", []),
        (["resumen"], "resumen", []),
    ],
)
def test_interpretar_comandos_validos(argv, comando, args):
    """RF-1.1: los tres comandos válidos devuelven (comando, args)."""
    assert interpretar(argv) == (comando, args)


@pytest.mark.parametrize(
    "argv, motivo",
    [
        ([], "falta el comando"),
        (["borrar"], 'el comando "borrar" no existe'),
        (["agregar"], "faltan el monto y la categoría"),
        (["agregar", "25"], "falta la categoría"),
        (["agregar", "25", "comida", "a", "b"], 'sobran argumentos: "b"'),
        (["listar", "x"], 'sobran argumentos: "x"'),
        (["resumen", "x", "y"], 'sobran argumentos: "x" "y"'),
    ],
)
def test_interpretar_uso_incorrecto(argv, motivo):
    """RF-9.1: sin comando, comando inexistente o cantidad incorrecta de argumentos es un error de uso."""
    with pytest.raises(ErrorUso) as error:
        interpretar(argv)
    assert error.value.motivo == motivo


@pytest.mark.parametrize(
    "argv",
    [
        ["agregar", "-5", "comida"],
        ["agregar", "-0.001", "comida"],
        ["agregar", "25", "comida", "-5 de descuento"],
    ],
)
def test_interpretar_guion_seguido_de_cifra_es_un_valor(argv):
    """RF-1.3: "-5" es un valor (lo rechazará la validación del monto con E-2), no una opción."""
    assert interpretar(argv) == ("agregar", argv[1:])


@pytest.mark.parametrize(
    "argv, opcion",
    [
        (["agregar", "5", "-ahorro"], "-ahorro"),
        (["listar", "-x"], "-x"),
        (["resumen", "--todo"], "--todo"),
        (["agregar", "5", "comida", "-"], "-"),
    ],
)
def test_interpretar_opcion_desconocida(argv, opcion):
    """RF-9.1: un argumento que empieza con "-" y no sigue con una cifra es una opción desconocida."""
    with pytest.raises(ErrorUso) as error:
        interpretar(argv)
    assert error.value.motivo == f'la opción "{opcion}" no existe'


@pytest.mark.parametrize(
    "argv, ayuda_de",
    [
        (["--ayuda"], []),
        (["agregar", "--ayuda"], ["agregar"]),
        (["agregar", "25", "--ayuda"], ["agregar"]),
        (["listar", "--ayuda"], ["listar"]),
        (["borrar", "--ayuda"], []),
    ],
)
def test_interpretar_ayuda(argv, ayuda_de):
    """RF-1.2: --ayuda, solo o después de un comando, pide la ayuda (la general si el comando no existe)."""
    assert interpretar(argv) == ("ayuda", ayuda_de)


def test_texto_ayuda_general():
    """RF-1.2, RF-9.2: la ayuda general en español, como en el plan."""
    assert texto_ayuda() == AYUDA_GENERAL


@pytest.mark.parametrize(
    "comando, esperado",
    [
        ("agregar", AYUDA_AGREGAR),
        ("listar", "Uso: gastos listar\nEjemplo: gastos listar"),
        ("resumen", "Uso: gastos resumen\nEjemplo: gastos resumen"),
    ],
)
def test_texto_ayuda_de_un_comando(comando, esperado):
    """RF-1.2: la ayuda de un comando muestra su línea Uso: y su ejemplo."""
    assert texto_ayuda(comando) == esperado


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["borrar"],
        ["agregar"],
        ["agregar", "25"],
        ["agregar", "25", "comida", "a", "b"],
        ["listar", "x"],
        ["agregar", "5", "-ahorro"],
        ["resumen", "--todo"],
    ],
)
def test_todo_error_de_uso_tiene_formato_e12(argv):
    """RF-10.3 (E-12), RF-9.2: "Error: <motivo>." seguido del texto de uso, que empieza con "Uso:"."""
    with pytest.raises(ErrorUso) as error:
        interpretar(argv)
    primera, *resto = str(error.value).split("\n")
    assert primera == f"Error: {error.value.motivo}."
    assert resto[0].startswith("Uso:")


def test_error_de_uso_muestra_la_ayuda_del_comando():
    """RF-10.3 (E-12): si el comando existe, se muestra su uso; si no, el uso general."""
    with pytest.raises(ErrorUso) as de_agregar:
        interpretar(["agregar", "25"])
    assert str(de_agregar.value) == "Error: falta la categoría.\n" + AYUDA_AGREGAR
    with pytest.raises(ErrorUso) as sin_comando:
        interpretar(["borrar"])
    assert str(sin_comando.value) == 'Error: el comando "borrar" no existe.\n' + AYUDA_GENERAL
