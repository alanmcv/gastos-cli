import pytest

from gastos.logica import (
    ErrorGastos,
    formatear_fecha,
    formatear_monto,
    normalizar_categoria,
    parsear_monto,
)

# Textos exactos del catálogo de la spec (RF-10.3).
E1 = "Error: falta el monto. Ejemplo: gastos agregar 25.50 comida"
E2 = "Error: el monto debe ser mayor que cero."
E3 = "Error: el monto puede tener como máximo 2 decimales."
E5 = "Error: el monto máximo por gasto es Bs 1000000.00."
E6 = "Error: falta la categoría."
E7 = (
    'Error: la categoría solo puede tener letras, cifras, espacios, "-" y "_", '
    "y debe empezar con una letra o una cifra."
)
E8 = "Error: la categoría puede tener como máximo 30 caracteres."


def e4(valor):
    return (
        f'Error: "{valor}" no es un monto válido. Usa solo cifras y, si quieres, '
        "un punto o una coma con hasta 2 decimales (ej.: 25.50)."
    )


def test_modulo_logica_se_puede_importar():
    """T01: el esqueleto del proyecto existe (sin RF)."""
    import gastos.logica  # noqa: F401


@pytest.mark.parametrize(
    "centavos, esperado",
    [
        (1, "Bs 0.01"),
        (2550, "Bs 25.50"),
        (100000000, "Bs 1000000.00"),
    ],
)
def test_formatear_monto(centavos, esperado):
    """RF-10.1: "Bs", 2 decimales, punto decimal y sin separador de miles."""
    assert formatear_monto(centavos) == esperado


def test_formatear_fecha():
    """RF-10.2: la fecha se muestra como DD/MM/AAAA."""
    assert formatear_fecha("2026-10-05") == "05/10/2026"


@pytest.mark.parametrize(
    "texto, centavos",
    [
        ("25", 2500),
        ("025", 2500),
        ("25.5", 2550),
        ("25,50", 2550),
        (" 25 ", 2500),
        (" 25\t", 2500),
        ("0.01", 1),
        ("1000000.00", 100000000),
    ],
)
def test_parsear_monto_valido(texto, centavos):
    """RF-3.1, RF-3.2, RF-3.3, RF-3.4: un monto válido se convierte en centavos exactos."""
    assert parsear_monto(texto) == centavos


@pytest.mark.parametrize(
    "texto, mensaje",
    [
        ("", E1),
        ("   ", E1),
        ("-5", E2),
        ("-0.001", E2),
        ("25.555", E3),
        ("0.001", E3),
        ("1.000", E3),
        ("+25", e4("+25")),
        (".50", e4(".50")),
        ("25.", e4("25.")),
        ("1e3", e4("1e3")),
        ("NaN", e4("NaN")),
        ("1 000", e4("1 000")),
        ("25 Bs", e4("25 Bs")),
        ("1.000,50", e4("1.000,50")),
        ("25,5,0", e4("25,5,0")),
        ("0", E2),
        ("00", E2),
        ("0.00", E2),
        ("0,0", E2),
        ("1000000.01", E5),
    ],
)
def test_parsear_monto_invalido_da_el_primer_error(texto, mensaje):
    """RF-3.5, RF-10.3: cada monto inválido da el primer error que corresponde, con su texto exacto."""
    with pytest.raises(ErrorGastos) as error:
        parsear_monto(texto)
    assert str(error.value) == mensaje


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("  Comida  Rápida ", "comida rápida"),
        ("comida\t\nrapida", "comida rapida"),
        ("CAFÉ", "café"),
        ("ÑANDÚ", "ñandú"),
        ("Café", "café"),  # "e" + tilde combinante queda como "é" (NFC)
    ],
)
def test_normalizar_categoria(texto, esperado):
    """RF-4.1: quita y colapsa espacios en blanco, aplica NFC y pasa a minúsculas."""
    assert normalizar_categoria(texto) == esperado


def test_normalizar_categoria_iguala_mayusculas_y_espacios():
    """RF-4.2: "COMIDA", "Comida" y " comida " son la misma categoría."""
    assert {normalizar_categoria(c) for c in ["COMIDA", "Comida", " comida "]} == {"comida"}


def test_normalizar_categoria_distingue_tildes():
    """RF-4.2: "Café" y "cafe" son categorías distintas."""
    assert normalizar_categoria("Café") != normalizar_categoria("cafe")


@pytest.mark.parametrize(
    "texto, mensaje",
    [
        ("   ", E6),
        ("", E6),
        ("_ahorro", E7),
        ("-ahorro", E7),
        ("comida🍕", E7),
        ("a/b", E7),
        ("x²", E7),
        ("a" * 31, E8),
    ],
)
def test_normalizar_categoria_invalida(texto, mensaje):
    """RF-4.3, RF-4.4, RF-4.5, RF-10.3: categoría vacía (E-6), con caracteres no permitidos (E-7) o larga (E-8)."""
    with pytest.raises(ErrorGastos) as error:
        normalizar_categoria(texto)
    assert str(error.value) == mensaje


@pytest.mark.parametrize("texto", ["a" * 30, "á" * 30, "comida-rapida_2", "9 ñandú über"])
def test_normalizar_categoria_valida_hasta_30_caracteres(texto):
    """RF-4.4, RF-4.5: letras con tilde, ñ, ü, cifras, espacios, "-" y "_"; 30 caracteres se aceptan."""
    assert normalizar_categoria(texto) == texto
