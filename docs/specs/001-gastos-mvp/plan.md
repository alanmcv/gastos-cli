# Plan 001 — gastos-cli MVP

**Estado:** aprobado (26/10/2026)
**Spec:** `docs/specs/001-gastos-mvp/spec.md` (versión 3)
**Constitución:** `docs/constitution.md`

Cada sección indica entre corchetes los RF que cubre.

## 1. Estructura de módulos

```
gastos/
  __init__.py      vacío
  __main__.py      permite ejecutar `python -m gastos`; solo llama a cli.main()
  logica.py        validación, normalización, filtro por mes, resumen y textos de salida
  almacen.py       lectura y guardado de los datos en JSON
  cli.py           interpretación de argumentos, impresión y códigos de salida
tests/
  test_logica.py
  test_almacen.py
  test_cli.py
pyproject.toml     solo la configuración de pytest (pythonpath = ["."], testpaths = ["tests"])
requirements-dev.txt   una línea: pytest
```

| Módulo | Responsabilidad | Puede usar | No puede usar | RF |
|---|---|---|---|---|
| `logica.py` | Funciones puras: reciben datos y devuelven datos o lanzan `ErrorGastos` | `re`, `unicodedata`, `datetime` | `print`, `input`, `argparse`, archivos | RF-2.4, RF-3, RF-4, RF-5, RF-6, RF-7, RF-10 |
| `almacen.py` | Leer, validar y guardar la lista de gastos | `json`, `os`, `pathlib`, `logica` | `print`, `input` | RF-8 |
| `cli.py` | Leer `argv`, llamar a la lógica y al almacén, imprimir y devolver el código de salida | `sys`, `datetime`, `logica`, `almacen` | reglas de negocio | RF-1, RF-2.1, RF-2.2, RF-9 |

**Funciones públicas de `logica.py`.** Cada una tiene sus propios tests (principio 4).

| Función | Qué hace | RF |
|---|---|---|
| `parsear_monto(texto) -> int` | Devuelve el monto en centavos o lanza E-1 a E-5 | RF-3 |
| `normalizar_categoria(texto) -> str` | Devuelve la categoría normalizada o lanza E-6 a E-8 | RF-4 |
| `normalizar_descripcion(texto) -> str` | Devuelve la descripción normalizada o lanza E-13 o E-9, en ese orden | RF-5 |
| `crear_gasto(monto, categoria, descripcion, hoy) -> dict` | Valida en orden (monto, categoría, descripción) y arma el gasto | RF-2.1, RF-2.3, RF-2.4 |
| `validar_gasto_guardado(gasto) -> bool` | Indica si un gasto leído del archivo cumple las reglas de la spec | RF-8.3 |
| `gastos_del_mes(gastos, anio, mes) -> list` | Filtra los gastos de un mes y año, conservando el orden | RF-6.1, RF-6.4, RF-7.1 |
| `resumir(gastos) -> (list, int)` | Devuelve las parejas (categoría, total) ordenadas y el total general | RF-7.2, RF-7.3, RF-7.4 |
| `formatear_monto(centavos) -> str` | Convierte `2550` en `Bs 25.50` | RF-10.1 |
| `formatear_fecha(iso) -> str` | Convierte `2026-10-26` en `26/10/2026` | RF-10.2 |
| `lineas_listado(gastos, anio, mes) -> list[str]` | Devuelve las líneas del listado, o M-2 si no hay gastos | RF-6 |
| `lineas_resumen(gastos, anio, mes) -> list[str]` | Devuelve las líneas del resumen, o M-2 si no hay gastos | RF-7 |

Un solo tipo de error, `ErrorGastos(Exception)`, transporta el texto exacto del catálogo (RF-10.3). La CLI lo imprime sin modificarlo.

## 2. Modelo de datos JSON [RF-8, RF-3.4]

- **Ubicación:** `gastos.json` en la carpeta personal del usuario (`Path.home()`), para que funcione desde cualquier carpeta.
- **Contenido:** una lista de gastos en orden de registro. La posición en la lista es el orden de RF-6.4.
- **Codificación:** UTF-8, con `ensure_ascii=False` (así las tildes se leen tal cual) e `indent=2` para que el archivo sea legible a mano.

```json
[
  {
    "fecha": "2026-10-03",
    "monto_centavos": 2550,
    "categoria": "comida",
    "descripcion": "almuerzo en la U"
  },
  {
    "fecha": "2026-10-03",
    "monto_centavos": 300,
    "categoria": "transporte",
    "descripcion": ""
  },
  {
    "fecha": "2026-10-26",
    "monto_centavos": 100000000,
    "categoria": "café",
    "descripcion": "matrícula ☕"
  }
]
```

| Campo | Tipo | Regla al leer (si se incumple, se muestra E-10) |
|---|---|---|
| `fecha` | texto `AAAA-MM-DD` | Exactamente ese patrón y una fecha real |
| `monto_centavos` | entero (no `bool`) | Entre 1 y 100 000 000 |
| `categoria` | texto | `normalizar_categoria(c) == c` |
| `descripcion` | texto | `normalizar_descripcion(d) == d` |

- Cualquier otra clave dentro de un gasto se ignora y se conserva al volver a guardar (RF-8.4).
- Si el nivel superior del archivo no es una lista, los datos se consideran dañados (E-10).

**Lectura:** `cargar(ruta) -> list` [RF-8.2, RF-8.3]

| Situación | Resultado |
|---|---|
| El archivo no existe | `[]` |
| `PermissionError` u otro `OSError` | E-10, motivo "sin permiso de lectura" o "error del sistema al leer" |
| 0 bytes o solo espacios | E-10, motivo "el archivo está vacío" |
| Falla `UnicodeDecodeError` o `json.JSONDecodeError` | E-10, motivo "el contenido no es JSON válido" |
| No es una lista, o algún gasto no pasa `validar_gasto_guardado` | E-10, motivo "el gasto número N no es válido" o "el contenido no es una lista de gastos" |

**Guardado:** `guardar(ruta, gastos)` [RF-8.5, RNF-3]
1. Escribir todo en `gastos.json.tmp`, en la misma carpeta.
2. Ejecutar `flush()` y `os.fsync()`.
3. Ejecutar `os.replace(tmp, ruta)`, que es atómico en Windows y en POSIX.

Ante un `OSError`, se borra el temporal si existe y se lanza E-11, con el motivo "sin permiso de escritura", "disco lleno" (`errno.ENOSPC`) o "error del sistema al escribir".

`agregar` siempre llama a `cargar()` antes de guardar. Por eso, con datos dañados, se detiene en E-10 y nunca sobrescribe el archivo (RF-8.3).

## 3. Algoritmo del resumen por categoría [RF-7]

```
función resumir(gastos_del_mes):
    totales ← diccionario vacío                 // categoria → centavos
    para cada g en gastos_del_mes:
        totales[g.categoria] ← totales.obtener(g.categoria, 0) + g.monto_centavos
    filas ← ordenar(parejas de totales,
                    clave = (−total, clave_alfabetica(categoria), categoria))
    total_general ← suma de todos los totales
    devolver filas, total_general

función clave_alfabetica(texto):                // RF-7.3
    resultado ← ""
    para cada c en texto:
        si c = "ñ":  resultado ← resultado + "n" + "\uffff"    // queda después de toda la n y antes de la o
        si no:       resultado ← resultado + c sin tilde       // NFD y quitar las marcas combinantes
    devolver resultado

función lineas_resumen(gastos, anio, mes):
    del_mes ← gastos_del_mes(gastos, anio, mes)
    si del_mes está vacío: devolver [M-2]                       // RF-7.5
    filas, total ← resumir(del_mes)
    devolver ["Resumen de " + nombre_mes(mes) + " de " + anio + ":"]
           + [categoria + ": " + formatear_monto(t) para cada (categoria, t) en filas]
           + ["Total: " + formatear_monto(total)]               // RF-7.1
```

- **Exactitud (RF-7.4, RNF-2):** todo se suma en enteros de centavos, y los enteros de Python no tienen límite. Nunca se usa `float`.
- **Costo:** O(n) para sumar y O(k log k) para ordenar las k categorías. 10 000 gastos se procesan en milisegundos (RNF-5).
- **Desempate final:** la clave `categoria` sin modificar desempata `cafe` y `café`, que tienen la misma clave alfabética. Como `e` (U+0065) va antes que `é` (U+00E9), la categoría sin tilde queda primero (RF-7.3).

## 4. Contrato de la CLI [RF-1, RF-2, RF-6, RF-7, RF-9, RF-10]

**Invocación:** `python -m gastos <comando> …`. El programa se presenta como `gastos` en la ayuda (RF-1.1).

| Entrada | Salida estándar (stdout) | Salida de errores (stderr) | Código | RF |
|---|---|---|---|---|
| `agregar <monto> <categoria> [descripcion]` válido | M-1 | — | 0 | RF-2.1, RF-2.2 |
| `agregar` con un dato inválido | — | primer error entre E-1 y E-9, o E-13 | 1 | RF-2.4, RF-3, RF-4, RF-5 |
| `listar` con gastos del mes | `Gastos de octubre de 2026:` y una línea por gasto | — | 0 | RF-6.1–6.5 |
| `listar` o `resumen` sin gastos del mes | M-2 | — | 0 | RF-6.6, RF-7.5 |
| `resumen` con gastos del mes | título, una línea por categoría y la línea `Total` | — | 0 | RF-7.1–7.4 |
| Cualquier comando con datos ilegibles | — | E-10 | 1 | RF-8.3 |
| `agregar` sin poder escribir | — | E-11 | 1 | RF-8.5 |
| `--ayuda`, o `<comando> --ayuda` | texto de ayuda | — | 0 | RF-1.2 |
| Sin comando, comando desconocido, faltan o sobran argumentos, opción desconocida | — | E-12 y el texto de uso | 2 | RF-9.1 |
| Ctrl+C durante cualquier comando | — | M-3 | 130 | RF-9.3 |

**Interpretación de los argumentos** (manual, sin `argparse`; ver la decisión D1):

```
función interpretar(argv):
    si argv está vacío:                      error de uso "falta el comando"
    si "--ayuda" está en argv:               mostrar la ayuda (de argv[0] si es un comando; si no, la general) y salir con 0
    comando, args ← argv[0], argv[1:]
    si comando no está en {agregar, listar, resumen}:   error de uso 'el comando "<comando>" no existe'
    para cada a en args:
        si a empieza con "-" y su segundo carácter no es una cifra:   error de uso 'la opción "<a>" no existe'   // RF-1.3
    si comando = agregar:
        si len(args) < 2:   error de uso "falta la categoría" (o "faltan el monto y la categoría")
        si len(args) > 3:   error de uso "sobran argumentos: <los de más>"
    si no:
        si len(args) > 0:   error de uso "sobran argumentos: <los de más>"
    devolver comando, args
```

**Texto de ayuda general** (RF-1.2, RF-9.2):

```
Uso:
  gastos agregar <monto> <categoria> [descripcion]   Registra un gasto con la fecha de hoy
  gastos listar                                      Muestra los gastos de este mes
  gastos resumen                                     Muestra el total por categoría de este mes
  gastos --ayuda                                     Muestra esta ayuda
Ejemplo: gastos agregar 25.50 comida "almuerzo en la U"
```

`<comando> --ayuda` muestra solo la línea `Uso:` de ese comando y su ejemplo.

**Firma de entrada:** `main(argv=None, ruta=None, hoy=None) -> int`.
- Los valores por defecto son `sys.argv[1:]`, `Path.home() / "gastos.json"` y `date.today()`.
- Los tests le pasan una ruta temporal y una fecha fija.
- `__main__.py` ejecuta `sys.exit(main())`.
- Al empezar, `main` reconfigura `sys.stdout` y `sys.stderr` a UTF-8, para que los emojis no fallen si la salida se redirige en Windows (RNF-6).
- `main` captura `KeyboardInterrupt`, escribe M-3 en stderr y devuelve 130 (RF-9.3).

## 5. Decisiones técnicas

| # | Decisión | Alternativa descartada | Por qué |
|---|---|---|---|
| D1 | Interpretar `argv` a mano (unas 30 líneas) | `argparse` | `argparse` escribe en inglés `usage:`, `error:`, `the following arguments are required` y `options:`. Traducirlo exige un catálogo `gettext` o modificar sus internos, y eso choca con RF-9.2 y con los textos exactos de RF-10.3. Con tres comandos posicionales, el código manual es más corto y lo entiende un junior. |
| D2 | Montos como enteros en centavos | `Decimal` o `float` | Lo exige el principio 5. `float` falla en `0.1 + 0.2`, y los enteros se guardan en JSON sin convertir. |
| D3 | Leer el monto con una expresión regular estricta, `[0-9]+([.,][0-9]{1,2})?` | `float(texto)` o `Decimal(texto)` | Esas funciones aceptan `1e3`, `nan`, `inf`, `+25` y `１２` (cifras Unicode), que RF-3.2 prohíbe. |
| D4 | Archivo con una lista de gastos | Un objeto con `version` y `gastos` | No hay migraciones previstas (YAGNI). RF-8.4 se cumple ignorando las claves de más dentro de cada gasto. |
| D5 | Fecha guardada como `AAAA-MM-DD` | Guardarla como `DD/MM/AAAA` | Es el estándar ISO, se ordena como texto y filtrar un mes es comparar el prefijo `AAAA-MM-`. El formato del usuario es solo para mostrar (RF-10.2). |
| D6 | Datos en `~/gastos.json` | `gastos.json` en la carpeta actual | En la carpeta actual, cada carpeta tendría sus propios gastos sin que el estudiante lo note. |
| D7 | Escribir un temporal, hacer `fsync` y luego `os.replace` | Escribir directo sobre el archivo | Lo exige RNF-3, y la constitución ya lo permite (principio 5). |
| D8 | Si un gasto guardado es inválido, todo el archivo se considera dañado | Saltar los gastos inválidos | Lo exige RF-8.3. Saltarlos haría que el siguiente guardado los borrara en silencio. |
| D9 | Una sola excepción, `ErrorGastos`, con el texto del catálogo | Una jerarquía de excepciones | Todos los errores de datos terminan igual: el texto va a stderr con código 1. Una clase por error no aporta nada. |
| D10 | `main(argv, ruta, hoy)` con parámetros inyectables | Usar `monkeypatch` sobre `date.today` y `Path.home` | Los tests son explícitos y no dependen de detalles internos. |
| D11 | Orden alfabético con `clave_alfabetica` propia | `locale.strxfrm` | El locale cambia según el sistema (`es_ES.UTF-8` frente a `Spanish_Spain`) y puede no estar instalado, así que los tests no serían reproducibles. |
| D12 | Normalizar a NFC antes de contar caracteres | Contar puntos de código sin normalizar | Una `é` escrita como `e` + tilde combinante contaría 2. Con NFC cuenta 1, como define la spec. |
| D13 | Validar las letras con `str.isalpha()` y las cifras con `0-9` | `str.isalnum()` | `isalnum()` acepta `²` y `٣`, y la spec habla solo de las cifras del 0 al 9. |
| D14 | Ejecutar con `python -m gastos` | Instalar el comando `gastos` desde `pyproject.toml` con un *entry point* | El *entry point* exige un backend de construcción (`setuptools`), que es una dependencia más y lo prohíbe el principio 1. Ver el ajuste A1. |
| D15 | Sin bloqueo de archivo | Un archivo de bloqueo | La concurrencia está fuera de alcance (spec, sección 7). |

## 6. Estrategia de tests [principio 4, sección 8 de la spec]

**Herramienta:** `pytest`, la única dependencia de desarrollo. Se ejecuta desde la raíz con `pytest`; `pyproject.toml` agrega la raíz al `pythonpath`.

**Ciclo por tarea:**
1. Escribir el test del criterio RF-x.y y verlo fallar (rojo).
2. Escribir el código mínimo que lo hace pasar (verde).
3. Ejecutar `pytest` completo.
4. Cerrar la tarea.

Cada test lleva en su nombre o en su docstring el RF que verifica, por ejemplo `test_rf3_5_monto_negativo_da_e2`.

| Archivo | Tipo | Qué cubre | Técnica |
|---|---|---|---|
| `test_logica.py` | Unitario y puro | RF-2.4, RF-3, RF-4, RF-5, RF-6, RF-7, RF-10 y casi toda la tabla de casos límite | `@pytest.mark.parametrize` con las filas de la sección 6 de la spec, más las comparaciones exactas con los textos M-x y E-x |
| `test_almacen.py` | Integración con disco | RF-8: archivo inexistente, vacío, JSON roto, no es lista, gasto inválido, claves de más, ida y vuelta con tildes y emoji. RNF-3: el original queda intacto si falla el guardado | `tmp_path`; `monkeypatch` de `os.replace` para que lance `OSError` o `KeyboardInterrupt`; `monkeypatch` de `Path.read_text` para que lance `PermissionError`, porque `chmod` no es fiable en Windows |
| `test_cli.py` | Extremo a extremo en proceso | RF-1, RF-2.1, RF-2.2, RF-9 y los códigos 0, 1 y 2: `main([...], ruta=tmp_path/"g.json", hoy=date(2026, 10, 26))` | `capsys` para separar stdout de stderr. Un test verifica que ninguna salida contenga `usage`, `error:` ni `required` (RF-9.2) |
| `test_cli.py` (1 test) | Humo, en otro proceso | La conexión `python -m gastos` → `__main__` → `main` | `subprocess.run` con `HOME` y `USERPROFILE` apuntando a `tmp_path` |

**Fechas:** los tests usan siempre `hoy` fijo y cubren los cambios de mes y de año, un mismo mes en años distintos y fechas futuras.

**Verificaciones manuales** (sección 5 de la spec):
- **RNF-5:** generar 10 000 gastos en una carpeta temporal y medir, en PowerShell:
  `$env:USERPROFILE="C:\temp\prueba"; Measure-Command { python -m gastos resumen }`
  El resultado se anota en la tarea.
- **RNF-6:** en PowerShell y en cmd, agregar `Café ☕` y una descripción con ñ, y luego listar.
- **RNF-4:** revisar que no se importe ningún módulo de red.

## 7. Ajustes a la spec

Todos se aprobaron e incorporaron en la spec versión 3 el 26/10/2026, con la recomendación propuesta en cada caso. No queda ninguno pendiente.

- **A1 [RF-1.1]:** la spec dice `gastos agregar …`, pero para que exista el comando `gastos` hay que instalarlo con `setuptools` (D14). Propuesta: que la spec diga que la invocación es `python -m gastos`, y que `gastos` sea el nombre que aparece en la ayuda.
- **A2 [RF-5.3]:** la spec no dice qué hacer con caracteres no imprimibles en la descripción (por ejemplo `\x07`). Propuesta: rechazarlos con un nuevo E-13, `Error: la descripción tiene caracteres no permitidos.`
- **A3 [RF-7.3]:** `cafe` y `café` empatan, porque se ignoran las tildes. Propuesta: desempatar poniendo primero la que no lleva tilde.
- **A4 [RF-10.3]:** si el usuario pulsa Ctrl+C, Python muestra un `KeyboardInterrupt` en inglés, y eso incumple RF-9.2. Propuesta: agregar M-3, `Operación cancelada.`, con código 130.

## 8. Cobertura de RF

| RF | Dónde se implementa | Dónde se prueba |
|---|---|---|
| RF-1 Sintaxis | `cli.interpretar`, textos de ayuda | `test_cli.py` |
| RF-2 Agregar | `logica.crear_gasto`, `cli.main` | `test_logica.py`, `test_cli.py` |
| RF-3 Monto | `logica.parsear_monto` | `test_logica.py` |
| RF-4 Categoría | `logica.normalizar_categoria` | `test_logica.py` |
| RF-5 Descripción | `logica.normalizar_descripcion` | `test_logica.py` |
| RF-6 Listar | `logica.gastos_del_mes`, `logica.lineas_listado` | `test_logica.py`, `test_cli.py` |
| RF-7 Resumen | `logica.resumir`, `logica.lineas_resumen` | `test_logica.py`, `test_cli.py` |
| RF-8 Persistencia | `almacen.cargar`, `almacen.guardar`, `logica.validar_gasto_guardado` | `test_almacen.py` |
| RF-9 Uso incorrecto | `cli.interpretar`; Ctrl+C en `cli.main` | `test_cli.py` |
| RF-10 Formato y mensajes | `logica.formatear_*`, constantes de mensajes en `logica` y `almacen` | `test_logica.py`, `test_almacen.py` |

## 9. Cumplimiento de la constitución

| Principio | Cómo se cumple |
|---|---|
| 1. Stack mínimo | Solo la biblioteca estándar (`re`, `unicodedata`, `json`, `os`, `pathlib`, `datetime`, `sys`). `pytest` va solo en `requirements-dev.txt`, y no hay backend de construcción (D14). |
| 2. La spec manda | Cada parte del plan cita su RF. Los vacíos encontrados se envían a la spec (sección 7) en lugar de decidirse en el código. |
| 3. Lógica separada de la interfaz | `logica.py` no imprime, no lee la entrada ni importa `argparse`. `cli.py` solo interpreta, llama y muestra. |
| 4. Tests primero | Hay un ciclo rojo-verde por tarea, cada función pública de `logica.py` tiene tests y `pytest` debe pasar completo para cerrar una tarea. |
| 5. Persistencia simple | Un único `~/gastos.json`, con un temporal solo mientras se guarda, y montos en `monto_centavos` como enteros. |
| 6. Todo en español | Los identificadores son ASCII en español (`monto_centavos`, `anio`, `categoria`) y los mensajes salen del catálogo de la spec. D1 evita los textos en inglés de `argparse`. |
