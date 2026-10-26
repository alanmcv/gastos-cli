# Tasks 001 — gastos-cli MVP

**Spec:** `spec.md` (versión 3) · **Plan:** `plan.md`

**Reglas de trabajo:**
- Se hace una tarea a la vez, en orden, y cada una dura como máximo 30 minutos.
- Cada tarea empieza con un test que falla. Luego se escribe el código mínimo para que pase y se ejecuta `pytest` completo.
- Una tarea se marca `[x]` solo si su "Hecho cuando" se cumple y `pytest` pasa completo.
- Los tests se nombran según lo que verifican, por ejemplo `test_parsear_monto_negativo_da_e2`, y su docstring cita el RF.

## Fase 0 — Preparación

- [x] **T00 · Cerrar la spec y el plan:** resolver los ajustes A1–A4 del plan, publicar la spec versión 3 y aprobar las dos. · RF-1.1, RF-5.4, RF-7.3, RF-9.3, RF-10.3
  - Hecho cuando: `spec.md` dice "Estado: aprobada" y "Versión: 3", `plan.md` dice "Estado: aprobado" y la sección 7 del plan ya no tiene ajustes pendientes.
- [x] **T01 · Esqueleto del proyecto:** crear `gastos/__init__.py`, `gastos/logica.py`, `tests/test_logica.py`, `pyproject.toml` (solo con la configuración de pytest) y `requirements-dev.txt`. · Sin RF (infraestructura) · Depende de T00
  - Test primero: un test que importa `gastos.logica` y falla porque el módulo no existe.
  - Hecho cuando: `pytest`, ejecutado desde la raíz, informa 1 test aprobado.

## Fase 1 — Lógica pura (`logica.py`)

- [x] **T02 · Formatos de salida:** `formatear_monto` y `formatear_fecha`. · RF-10.1, RF-10.2 · Depende de T01
  - Hecho cuando: los tests confirman que `1` → `Bs 0.01`, `2550` → `Bs 25.50`, `100000000` → `Bs 1000000.00` y `"2026-10-05"` → `05/10/2026`.
- [x] **T03 · `parsear_monto`, montos válidos.** · RF-3.1, RF-3.2, RF-3.3, RF-3.4 · Depende de T01
  - Hecho cuando: un test parametrizado confirma que `25` → 2500, `025` → 2500, `25.5` → 2550, `25,50` → 2550, ` 25 ` → 2500, `0.01` → 1 y `1000000.00` → 100000000.
- [x] **T04 · `parsear_monto`, errores en orden:** se crean las constantes E-1 a E-5 con el texto exacto del catálogo. · RF-3.5, RF-10.3 · Depende de T03
  - Hecho cuando: un test parametrizado confirma que cada monto inválido de la sección 6 de la spec lanza `ErrorGastos` con el texto exacto esperado. Incluye `""`, `-0.001`, `1.000`, `1.000,50`, `1e3`, `00` y `1000000.01`.
- [x] **T05 · `normalizar_categoria`, normalización:** quitar espacios de los extremos, colapsar los internos, pasar a NFC y a minúsculas. · RF-4.1, RF-4.2 · Depende de T01
  - Hecho cuando: los tests confirman que `"  Comida  Rápida "` → `"comida rápida"`, que `"COMIDA"`, `"Comida"` y `" comida "` dan el mismo resultado, y que `"Café"` es distinto de `"cafe"`.
- [x] **T06 · `normalizar_categoria`, errores:** E-6, E-7 y E-8. · RF-4.3, RF-4.4, RF-4.5, RF-10.3 · Depende de T05
  - Hecho cuando: los tests confirman que `"   "` → E-6, que `"_ahorro"`, `"comida🍕"`, `"a/b"` y `"x²"` → E-7, y que una categoría de 30 caracteres se acepta y una de 31 → E-8.
- [x] **T07 · `normalizar_descripcion`.** · RF-5.1, RF-5.2, RF-5.3, RF-5.4, RF-5.5, RF-10.3 · Depende de T05
  - Hecho cuando: los tests confirman que `"   "` → `""`, que `"a\nb"` → `"a b"`, que se conservan las mayúsculas, que 100 caracteres con tildes o emojis se aceptan, que 101 → E-9, que `"a\x07b"` → E-13 y que 101 caracteres con `\x07` → E-13.
- [x] **T08 · `crear_gasto`.** · RF-2.1, RF-2.3, RF-2.4 · Depende de T04, T06 y T07
  - Hecho cuando:
    - con `hoy=date(2026,10,26)` se obtiene `{"fecha": "2026-10-26", "monto_centavos": …, "categoria": …, "descripcion": ""}`;
    - un monto inválido junto con una categoría inválida lanza solo el error del monto;
    - una categoría inválida junto con una descripción inválida lanza solo el error de la categoría.
- [x] **T09 · `validar_gasto_guardado`.** · RF-8.3, RF-8.4 · Depende de T08
  - Hecho cuando: un gasto válido, incluso con claves de más, da `True`. Da `False` cada uno de estos casos:
    - fecha `2026-13-01` o `20261026`;
    - monto `0`, `True`, `25.5` o `100000001`;
    - categoría sin normalizar (`"Comida"`);
    - descripción sin normalizar;
    - falta una clave obligatoria.
- [x] **T10 · `gastos_del_mes`.** · RF-6.1, RF-6.4, RF-7.1 · Depende de T01
  - Hecho cuando: los tests de cambio de mes, de año y de un mismo mes en años distintos dan lo que dice la spec, y un gasto con fecha futura dentro del mes aparece en su orden de registro.
- [x] **T11 · `resumir` y el orden alfabético.** · RF-7.2, RF-7.3, RF-7.4, RNF-2 · Depende de T10
  - Hecho cuando: los tests confirman que:
    - las categorías se ordenan de mayor a menor total;
    - el empate se ordena `árbol`, `nube`, `ñandú`;
    - en el empate `café`/`cafe`, `cafe` va primero;
    - `0.10 + 0.20` da 30 centavos;
    - 3 gastos de 1000000 dan 300000000 centavos.
- [x] **T12 · `lineas_listado` y M-2.** · RF-6.1, RF-6.2, RF-6.3, RF-6.5, RF-6.6, RF-10.3 · Depende de T02 y T10
  - Hecho cuando: los tests confirman las líneas exactas `Gastos de octubre de 2026:` y `03/10/2026 | comida | Bs 25.50 | almuerzo`, una descripción vacía mostrada como `-`, y M-2 cuando no hay gastos del mes.
- [x] **T13 · `lineas_resumen`.** · RF-7.1, RF-7.5, RF-10.3 · Depende de T11 y T12
  - Hecho cuando: los tests confirman las líneas exactas `Resumen de octubre de 2026:`, `comida: Bs 25.50` y `Total: Bs …`, que una sola categoría da 3 líneas y que sin gastos se obtiene M-2.

## Fase 2 — Almacén (`almacen.py`)

- [x] **T14 · `cargar` y `guardar`, casos normales.** · RF-8.1, RF-8.2, RF-8.4 · Depende de T09
  - Hecho cuando: en `tmp_path`, un archivo inexistente da `[]`, y una ida y vuelta con `café ☕` y una clave de más devuelve exactamente lo que se guardó, con el JSON en UTF-8 legible (sin `é`).
- [ ] **T15 · `cargar`, datos ilegibles (E-10).** · RF-8.3, RF-10.3 · Depende de T14
  - Hecho cuando: cada uno de estos casos lanza E-10 con su motivo en español, y el contenido del archivo queda idéntico byte a byte:
    - archivo de 0 bytes;
    - JSON roto;
    - bytes que no son UTF-8 válido;
    - un objeto en lugar de una lista;
    - un gasto inválido;
    - `PermissionError`, simulado con `monkeypatch`.
- [ ] **T16 · `guardar` atómico y E-11.** · RF-8.5, RNF-3, RF-10.3 · Depende de T14
  - Hecho cuando: con `os.replace` parcheado para lanzar `OSError` o `KeyboardInterrupt`, el archivo original queda intacto y el `.tmp` no queda en la carpeta. Además, `PermissionError` da el motivo "sin permiso de escritura" y `errno.ENOSPC` da "disco lleno".

## Fase 3 — CLI (`cli.py`)

- [ ] **T17 · `interpretar`, comandos y cantidad de argumentos.** · RF-1.1, RF-9.1 · Depende de T01
  - Hecho cuando: los tests confirman que `[]`, `["borrar"]`, `["agregar", "25"]`, `["agregar", "25", "comida", "a", "b"]` y `["listar", "x"]` dan un error de uso con su motivo en español, y que los 3 comandos válidos devuelven `(comando, args)`.
- [ ] **T18 · `interpretar`, opciones y valores negativos.** · RF-1.3, RF-9.1 · Depende de T17
  - Hecho cuando: los tests confirman que `["agregar", "-5", "comida"]` se acepta como valor, y que `["agregar", "5", "-ahorro"]` y `["listar", "-x"]` dan el error de uso `la opción "…" no existe`.
- [ ] **T19 · Ayuda y E-12.** · RF-1.2, RF-9.2, RF-10.3 · Depende de T18
  - Hecho cuando: los tests confirman que `--ayuda` muestra el texto general del plan, que `agregar --ayuda` muestra la ayuda de `agregar` y que todo error de uso empieza con `Error: ` y contiene una línea `Uso:`.
- [ ] **T20 · `main` con `agregar`.** · RF-2.1, RF-2.2, RF-2.4, RF-8.2 · Depende de T08, T16 y T19
  - Hecho cuando: con `main(["agregar", "25,5", "Comida"], ruta=tmp, hoy=date(2026,10,26))` se obtienen el código 0, `Gasto registrado: Bs 25.50 en comida el 26/10/2026.` en stdout y el gasto guardado. Un monto inválido da el código 1, el error en stderr y ningún archivo creado.
- [ ] **T21 · `main` con `listar` y `resumen`.** · RF-6, RF-7, RF-8.1 · Depende de T13 y T20
  - Hecho cuando: en el primer uso, los dos comandos dan M-2 y el código 0. Después de 3 llamadas a `agregar`, la salida coincide línea por línea con lo esperado. Un gasto de septiembre no aparece en octubre.
- [ ] **T22 · `main` con errores de datos y de uso.** · RF-8.3, RF-8.5, RF-9.1, RF-9.2 · Depende de T15 y T21
  - Hecho cuando: los tests confirman que:
    - con datos dañados, los 3 comandos dan E-10 en stderr y el código 1, y el archivo no cambia;
    - un fallo al guardar da E-11 y el código 1;
    - un error de uso da el código 2;
    - un test recorre todas las salidas y no encuentra `usage`, `error:` ni `required`.
- [ ] **T23 · Punto de entrada.** Crear `__main__.py`, reconfigurar la salida a UTF-8 y agregar un test de humo con `subprocess`. · RF-1.1, RNF-6 · Depende de T22
  - Hecho cuando: `subprocess.run([sys.executable, "-m", "gastos", "listar"])`, con `HOME` y `USERPROFILE` apuntando a `tmp_path`, termina con código 0 y muestra M-2 en stdout.
- [ ] **T24 · Ctrl+C (M-3).** · RF-9.3, RF-10.3 · Depende de T23
  - Hecho cuando: un `KeyboardInterrupt` simulado dentro de `main` da `Operación cancelada.` en stderr y el código 130, sin ningún traceback.

## Fase 4 — Verificación y cierre

- [ ] **T25 · Verificaciones manuales.** · RNF-4, RNF-5, RNF-6 · Depende de T23
  - Hecho cuando: los resultados quedan anotados debajo de esta tarea:
    - el tiempo de `resumen` con 10 000 gastos, que debe ser menor a 1 s;
    - una captura o la salida de `Café ☕` y la ñ en PowerShell y en cmd;
    - una búsqueda en `gastos/` que confirme que no se importa `socket`, `urllib` ni `http`.
- [ ] **T26 · Cierre de la spec.** · Todos los RF · Depende de T00–T25
  - Hecho cuando: cada RF-x.y aparece en el docstring de al menos un test, cada fila de la sección 6 de la spec tiene un test o una verificación manual anotada, se demostró el flujo completo `agregar` → `listar` → `resumen` a mano, `pytest` pasa completo y se cumple la lista de la sección 8 de la spec.

## Cobertura

| RF | Tareas |
|---|---|
| RF-1 | T17, T18, T19, T23 |
| RF-2 | T08, T20 |
| RF-3 | T03, T04 |
| RF-4 | T05, T06 |
| RF-5 | T07 |
| RF-6 | T10, T12, T21 |
| RF-7 | T11, T13, T21 |
| RF-8 | T09, T14, T15, T16, T20, T22 |
| RF-9 | T17, T18, T19, T22, T24 |
| RF-10 | T02, T04, T06, T12, T13, T15, T16, T19 |
| RNF-2, RNF-3 | T11, T16 |
| RNF-4, RNF-5, RNF-6 | T23, T25 |
