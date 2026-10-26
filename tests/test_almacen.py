from gastos.almacen import cargar, guardar

GASTOS = [
    {"fecha": "2026-10-03", "monto_centavos": 2550, "categoria": "café", "descripcion": "almuerzo ☕"},
    {"fecha": "2026-10-04", "monto_centavos": 300, "categoria": "transporte", "descripcion": "", "nota": "extra"},
]


def test_cargar_sin_datos_guardados_devuelve_lista_vacia(tmp_path):
    """RF-8.2: si todavía no hay datos guardados, se trabaja como si no hubiera gastos."""
    assert cargar(tmp_path / "gastos.json") == []


def test_guardar_y_cargar_ida_y_vuelta(tmp_path):
    """RF-8.1, RF-8.4: lo guardado se recupera igual, incluidas las claves de más."""
    ruta = tmp_path / "gastos.json"
    guardar(ruta, GASTOS)
    assert cargar(ruta) == GASTOS


def test_guardar_escribe_utf8_legible(tmp_path):
    """RF-8.1: el JSON se guarda en UTF-8 con las tildes y emojis tal cual (sin \\u00e9)."""
    ruta = tmp_path / "gastos.json"
    guardar(ruta, GASTOS)
    texto = ruta.read_text(encoding="utf-8")
    assert "café" in texto and "☕" in texto
    assert "\\u" not in texto
