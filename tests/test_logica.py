import pytest

from gastos.logica import formatear_fecha, formatear_monto, parsear_monto


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
