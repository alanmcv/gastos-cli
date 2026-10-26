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
