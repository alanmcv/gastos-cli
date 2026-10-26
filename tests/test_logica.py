from datetime import date

import pytest

from gastos.logica import (
    ErrorGastos,
    crear_gasto,
    formatear_fecha,
    formatear_monto,
    gastos_del_mes,
    lineas_listado,
    normalizar_categoria,
    normalizar_descripcion,
    parsear_monto,
    resumir,
    validar_gasto_guardado,
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
E9 = "Error: la descripción puede tener como máximo 100 caracteres."
E13 = "Error: la descripción tiene caracteres no permitidos."


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


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("   ", ""),
        ("", ""),
        ("a\nb", "a b"),
        ("  Almuerzo  en la U ", "Almuerzo en la U"),
        ("Matrícula ☕ 🍕", "Matrícula ☕ 🍕"),
        ("ñ" * 50 + "🍕" * 50, "ñ" * 50 + "🍕" * 50),
    ],
)
def test_normalizar_descripcion(texto, esperado):
    """RF-5.1, RF-5.2, RF-5.3, RF-5.5: normaliza espacios, conserva mayúsculas y emojis; 100 caracteres se aceptan."""
    assert normalizar_descripcion(texto) == esperado


@pytest.mark.parametrize(
    "texto, mensaje",
    [
        ("a" * 101, E9),
        ("a\x07b", E13),
        ("a" * 100 + "\x07", E13),
    ],
)
def test_normalizar_descripcion_invalida(texto, mensaje):
    """RF-5.4, RF-5.5, RF-10.3: no imprimibles dan E-13 (antes que el largo) y más de 100 caracteres dan E-9."""
    with pytest.raises(ErrorGastos) as error:
        normalizar_descripcion(texto)
    assert str(error.value) == mensaje


HOY = date(2026, 10, 26)


def test_crear_gasto_con_la_fecha_de_hoy_y_datos_normalizados():
    """RF-2.1, RF-2.3: el gasto lleva la fecha actual y, sin descripción, queda vacía."""
    assert crear_gasto(" 25,5 ", "  Comida ", "", HOY) == {
        "fecha": "2026-10-26",
        "monto_centavos": 2550,
        "categoria": "comida",
        "descripcion": "",
    }


def test_crear_gasto_normaliza_la_descripcion():
    """RF-2.1: la descripción se guarda normalizada."""
    assert crear_gasto("3", "transporte", "  micro  a la U ", HOY)["descripcion"] == "micro a la U"


@pytest.mark.parametrize(
    "monto, categoria, descripcion, mensaje",
    [
        ("-5", "_mal", "a" * 101, E2),  # monto, categoría y descripción inválidos: solo el del monto
        ("abc", "", "", e4("abc")),
        ("25", "_mal", "a" * 101, E7),  # categoría y descripción inválidas: solo el de la categoría
        ("25", "comida", "a\x07", E13),
    ],
)
def test_crear_gasto_muestra_solo_el_primer_error(monto, categoria, descripcion, mensaje):
    """RF-2.4: se valida el monto, luego la categoría y luego la descripción; solo sale el primer error."""
    with pytest.raises(ErrorGastos) as error:
        crear_gasto(monto, categoria, descripcion, HOY)
    assert str(error.value) == mensaje


GASTO_VALIDO = {
    "fecha": "2026-10-26",
    "monto_centavos": 2550,
    "categoria": "café",
    "descripcion": "almuerzo ☕",
}


def test_validar_gasto_guardado_acepta_un_gasto_valido():
    """RF-8.3: un gasto que cumple las reglas de la spec es válido."""
    assert validar_gasto_guardado(GASTO_VALIDO) is True


def test_validar_gasto_guardado_ignora_claves_de_mas():
    """RF-8.4: la información adicional no invalida el gasto."""
    assert validar_gasto_guardado({**GASTO_VALIDO, "nota": "extra"}) is True


@pytest.mark.parametrize(
    "cambios",
    [
        {"fecha": "2026-13-01"},
        {"fecha": "20261026"},
        {"fecha": 20261026},
        {"monto_centavos": 0},
        {"monto_centavos": True},
        {"monto_centavos": 25.5},
        {"monto_centavos": "2550"},
        {"monto_centavos": 100000001},
        {"categoria": "Comida"},
        {"categoria": "_mal"},
        {"categoria": 5},
        {"descripcion": "  sin normalizar"},
        {"descripcion": "a" * 101},
        {"descripcion": None},
    ],
)
def test_validar_gasto_guardado_rechaza_un_campo_invalido(cambios):
    """RF-8.3: un campo que incumple las reglas de la spec invalida el gasto."""
    assert validar_gasto_guardado({**GASTO_VALIDO, **cambios}) is False


@pytest.mark.parametrize("clave", ["fecha", "monto_centavos", "categoria", "descripcion"])
def test_validar_gasto_guardado_rechaza_si_falta_una_clave(clave):
    """RF-8.3: si falta una clave obligatoria, el gasto no es válido."""
    gasto = dict(GASTO_VALIDO)
    del gasto[clave]
    assert validar_gasto_guardado(gasto) is False


@pytest.mark.parametrize("gasto", ["texto", 5, None, ["2026-10-26", 2550]])
def test_validar_gasto_guardado_rechaza_lo_que_no_es_un_objeto(gasto):
    """RF-8.3: un elemento que no es un objeto JSON no es un gasto."""
    assert validar_gasto_guardado(gasto) is False


def gasto(fecha, monto_centavos=100, categoria="comida", descripcion=""):
    return {
        "fecha": fecha,
        "monto_centavos": monto_centavos,
        "categoria": categoria,
        "descripcion": descripcion,
    }


def test_gastos_del_mes_filtra_por_mes_y_anio_conservando_el_orden():
    """RF-6.1, RF-6.4, RF-7.1: solo el mes y año pedidos, en orden de registro (aunque una fecha sea futura)."""
    futuro = gasto("2026-10-30")  # registrado antes que el del día 1 (reloj alterado)
    primero = gasto("2026-10-01")
    ultimo = gasto("2026-10-31")
    gastos = [
        gasto("2026-09-30"),
        futuro,
        gasto("2025-10-15"),
        primero,
        gasto("2026-11-01"),
        ultimo,
    ]
    assert gastos_del_mes(gastos, 2026, 10) == [futuro, primero, ultimo]


def test_gastos_del_mes_en_cambio_de_anio():
    """RF-6.1: un gasto de diciembre de 2026 no aparece en enero de 2027."""
    enero = gasto("2027-01-01")
    assert gastos_del_mes([gasto("2026-12-31"), enero], 2027, 1) == [enero]


def test_gastos_del_mes_sin_gastos():
    """RF-6.1: si no hay gastos ese mes, la lista queda vacía."""
    assert gastos_del_mes([gasto("2026-09-30")], 2026, 10) == []


def gastos_por_categoria(*pares):
    """Arma un gasto de octubre de 2026 por cada pareja (categoria, centavos)."""
    return [gasto("2026-10-26", centavos, categoria) for categoria, centavos in pares]


def test_resumir_suma_por_categoria_y_ordena_de_mayor_a_menor():
    """RF-7.2: totales por categoría, de mayor a menor, y total general."""
    gastos = gastos_por_categoria(
        ("transporte", 1000), ("comida", 1500), ("ocio", 2000), ("comida", 1500)
    )
    assert resumir(gastos) == ([("comida", 3000), ("ocio", 2000), ("transporte", 1000)], 6000)


@pytest.mark.parametrize(
    "categorias, orden_esperado",
    [
        (["ñandú", "nube", "árbol"], ["árbol", "nube", "ñandú"]),
        (["café", "cafe"], ["cafe", "café"]),
        (["ña", "nz"], ["nz", "ña"]),
        (["oso", "ñu"], ["ñu", "oso"]),
        (["über", "uva"], ["über", "uva"]),
    ],
)
def test_resumir_desempata_alfabeticamente(categorias, orden_esperado):
    """RF-7.3: empate alfabético sin tildes, ñ después de la n; si solo difieren en tildes, va primero la que no lleva."""
    filas, _ = resumir(gastos_por_categoria(*[(c, 500) for c in categorias]))
    assert [categoria for categoria, _ in filas] == orden_esperado


def test_resumir_es_exacto_al_centavo():
    """RF-7.4, RNF-2: 0.10 + 0.20 da exactamente 0.30."""
    assert resumir(gastos_por_categoria(("comida", 10), ("comida", 20))) == ([("comida", 30)], 30)


def test_resumir_supera_el_monto_maximo_de_un_gasto():
    """RF-7.4: 3 gastos de 1000000 dan un total de 3000000, sin límite superior."""
    gastos = gastos_por_categoria(*[("matricula", 100000000)] * 3)
    assert resumir(gastos) == ([("matricula", 300000000)], 300000000)


def test_lineas_listado():
    """RF-6.1, RF-6.3, RF-10.3: título y una línea por gasto del mes; la descripción vacía se muestra como "-"."""
    gastos = [
        gasto("2026-10-03", 2550, "comida", "almuerzo"),
        gasto("2026-09-30", 999, "ocio", "no aparece"),
        gasto("2026-10-05", 300, "transporte", ""),
    ]
    assert lineas_listado(gastos, 2026, 10) == [
        "Gastos de octubre de 2026:",
        "03/10/2026 | comida | Bs 25.50 | almuerzo",
        "05/10/2026 | transporte | Bs 3.00 | -",
    ]


def test_lineas_listado_muestra_todos_los_gastos_sin_recortar():
    """RF-6.5: el listado no se pagina ni se recorta."""
    gastos = [gasto("2026-10-26") for _ in range(500)]
    assert len(lineas_listado(gastos, 2026, 10)) == 501


@pytest.mark.parametrize(
    "mes, nombre",
    [
        (1, "enero"), (2, "febrero"), (3, "marzo"), (4, "abril"),
        (5, "mayo"), (6, "junio"), (7, "julio"), (8, "agosto"),
        (9, "septiembre"), (10, "octubre"), (11, "noviembre"), (12, "diciembre"),
    ],
)
def test_lineas_listado_sin_gastos_del_mes_da_m2(mes, nombre):
    """RF-6.2, RF-6.6, RF-10.3: sin gastos del mes se muestra M-2, con el mes en español y minúsculas."""
    assert lineas_listado([gasto("2025-10-15")], 2026, mes) == [
        f"No hay gastos registrados en {nombre} de 2026."
    ]
