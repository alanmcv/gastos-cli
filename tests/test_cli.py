import pytest

from gastos.cli import ErrorUso, interpretar


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
