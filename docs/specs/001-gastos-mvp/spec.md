# Spec 001 — gastos-cli MVP

**Estado:** aprobada (26/10/2026)
**Versión:** 3 (26/10/2026). Incorpora los ajustes A1–A4 del plan. La versión 2 corrigió los hallazgos de la revisión de QA.
**Constitución:** `docs/constitution.md`

## 1. Contexto y objetivo

Un estudiante gasta pequeñas cantidades a diario (comida, transporte, fotocopias) y a fin de mes no sabe en qué se le fue el dinero. Las apps de finanzas son pesadas para algo tan simple.

**Objetivo:** que el estudiante registre un gasto en segundos desde la terminal y pueda ver, en cualquier momento, qué gastó este mes y cuánto lleva por categoría.

## 2. Usuarios

- **Estudiante:** una sola persona que usa la herramienta en su propio equipo. Sabe abrir una terminal y escribir un comando, pero no es necesariamente programador.
- No hay varios usuarios, cuentas ni datos compartidos.

## 3. Historias de usuario

- **HU-1:** Como estudiante, quiero registrar un gasto con su monto, su categoría y una descripción opcional, para no olvidarlo.
- **HU-2:** Como estudiante, quiero listar los gastos del mes actual, para revisar en qué gasté.
- **HU-3:** Como estudiante, quiero ver el total por categoría del mes actual, para saber en qué se me va el dinero.

## 4. Requisitos funcionales

Notación EARS: *El sistema deberá…* (siempre), *Cuando…* (ante un evento), *Mientras…* (en un estado), *Si… entonces…* (ante un caso no deseado).

**Definiciones**
- **Fecha actual:** la fecha según el reloj y la zona horaria del equipo en el momento de ejecutar el comando.
- **Mes actual:** el mes y el año de la fecha actual. Octubre de 2025 y octubre de 2026 son meses distintos.
- **Espacio en blanco:** un espacio, una tabulación, un salto de línea o un espacio duro.
- **Carácter:** un carácter Unicode. `á`, `ñ` y un emoji simple cuentan como 1 carácter cada uno.
- **Mensaje de error:** un mensaje del catálogo de RF-10.

### RF-1 Sintaxis de los comandos
- **RF-1.1** El sistema se ejecutará con `python -m gastos`. En esta spec, `gastos` abrevia esa invocación y es el nombre que aparece en la ayuda. El sistema deberá ofrecer exactamente estos comandos:
  - `gastos agregar <monto> <categoria> [descripcion]`
  - `gastos listar`
  - `gastos resumen`
  - `gastos --ayuda`
- **RF-1.2** Cuando el usuario escriba `--ayuda`, solo o después de un comando, el sistema deberá mostrar en español cómo se usan el programa o ese comando, y terminar con código 0.
- **RF-1.3** El sistema deberá tratar un argumento que empieza con `-` seguido de una cifra (por ejemplo `-5`) como un valor, no como una opción.

### RF-2 Agregar un gasto (HU-1)
- **RF-2.1** Cuando el usuario agregue un gasto válido, el sistema deberá guardarlo con la fecha actual.
- **RF-2.2** Cuando el gasto se guarde, el sistema deberá mostrar el mensaje M-1 y terminar con código 0.
- **RF-2.3** Cuando el usuario no indique una descripción, el sistema deberá guardar el gasto con la descripción vacía.
- **RF-2.4** El sistema deberá validar el monto, luego la categoría y luego la descripción. Si uno de esos datos no es válido, entonces deberá mostrar solo el primer error encontrado, no guardar nada y terminar con código 1.

### RF-3 Validar el monto
- **RF-3.1** El sistema deberá ignorar los espacios en blanco al inicio y al final del monto.
- **RF-3.2** El sistema deberá aceptar como monto solo cifras del 0 al 9, seguidas opcionalmente de un único separador decimal (`.` o `,`) y de 1 o 2 cifras. Ejemplos válidos: `25`, `025`, `25.5`, `25,50`.
- **RF-3.3** El sistema deberá interpretar la coma igual que el punto: `25,5`, `25.5` y `25.50` son el mismo valor.
- **RF-3.4** El sistema deberá conservar el valor exacto del monto, sin errores de redondeo. No conserva el texto tal como se escribió.
- **RF-3.5** Si el monto no es válido, entonces el sistema deberá rechazarlo con el primer error que corresponda, en este orden:
  1. El monto está vacío: E-1.
  2. El monto empieza con `-`: E-2.
  3. Tiene un único separador seguido de 3 o más cifras: E-3.
  4. Tiene cualquier otro formato que no cumpla RF-3.2: E-4.
  5. Su valor es cero: E-2.
  6. Su valor supera 1000000 (el valor 1000000 está permitido): E-5.

### RF-4 Validar y normalizar la categoría
- **RF-4.1** Cuando el usuario ingrese una categoría, el sistema deberá normalizarla antes de validarla y guardarla:
  - quitar los espacios en blanco del inicio y del final;
  - reemplazar cada grupo de espacios en blanco internos por un solo espacio;
  - pasarla a minúsculas, incluidas las letras con tilde y la ñ (`CAFÉ` → `café`).
- **RF-4.2** El sistema deberá tratar como la misma categoría a las que coinciden después de normalizarse: `Comida`, `  comida ` y `COMIDA`. En cambio, `café` y `cafe` son categorías distintas.
- **RF-4.3** Si la categoría queda vacía después de normalizarse, entonces el sistema deberá rechazarla con E-6.
- **RF-4.4** Si la categoría contiene algo distinto de letras (incluidas las letras con tilde, la ñ y la ü), cifras, espacios, `-` o `_`, o si no empieza con una letra o una cifra, entonces el sistema deberá rechazarla con E-7.
- **RF-4.5** Si la categoría normalizada tiene más de 30 caracteres, entonces el sistema deberá rechazarla con E-8.

### RF-5 Validar y normalizar la descripción
- **RF-5.1** Cuando el usuario ingrese una descripción, el sistema deberá normalizarla igual que la categoría (RF-4.1), pero sin pasarla a minúsculas.
- **RF-5.2** El sistema deberá tratar como vacía una descripción que queda vacía después de normalizarse.
- **RF-5.3** El sistema deberá aceptar en la descripción cualquier carácter imprimible, incluidos los emojis.
- **RF-5.4** Si la descripción normalizada contiene un carácter no imprimible (por ejemplo `\x07`), entonces el sistema deberá rechazarla con E-13. Esta comprobación va antes que la de RF-5.5.
- **RF-5.5** Si la descripción normalizada tiene más de 100 caracteres, entonces el sistema deberá rechazarla con E-9.

### RF-6 Listar los gastos del mes (HU-2)
- **RF-6.1** Cuando el usuario ejecute `gastos listar`, el sistema deberá mostrar la línea `Gastos de <mes> de <año>:` y, debajo, una línea por cada gasto del mes actual con el formato `DD/MM/AAAA | categoria | Bs 0.00 | descripcion`.
- **RF-6.2** El sistema deberá escribir el mes en español y en minúsculas, por ejemplo `octubre de 2026`.
- **RF-6.3** El sistema deberá mostrar `-` en lugar de una descripción vacía.
- **RF-6.4** El sistema deberá mostrar los gastos en el orden en que se registraron, del más antiguo al más reciente, aunque la fecha de alguno sea posterior a la actual.
- **RF-6.5** El sistema deberá mostrar todos los gastos del mes, sin paginar ni recortar.
- **RF-6.6** Cuando no haya gastos en el mes actual, el sistema deberá mostrar el mensaje M-2 y terminar con código 0.

### RF-7 Resumen por categoría (HU-3)
- **RF-7.1** Cuando el usuario ejecute `gastos resumen`, el sistema deberá mostrar:
  - la línea `Resumen de <mes> de <año>:`;
  - una línea `categoria: Bs 0.00` por cada categoría con gastos en el mes actual;
  - una última línea `Total: Bs 0.00` con la suma de todo el mes.
- **RF-7.2** El sistema deberá ordenar las categorías de mayor a menor total.
- **RF-7.3** Si dos o más categorías tienen el mismo total, el sistema deberá ordenarlas alfabéticamente, ignorando las tildes y poniendo la ñ después de la n. Si siguen empatadas porque solo se diferencian en las tildes (`cafe` y `café`), primero va la que no lleva tilde.
- **RF-7.4** El sistema deberá calcular los totales de forma exacta, sin límite superior y aunque superen el monto máximo de un gasto.
- **RF-7.5** Cuando no haya gastos en el mes actual, el sistema deberá mostrar el mensaje M-2 y terminar con código 0.

### RF-8 Persistencia de los datos
- **RF-8.1** El sistema deberá conservar los gastos de una ejecución a otra.
- **RF-8.2** Mientras no existan datos guardados, el sistema deberá funcionar como si no hubiera gastos y deberá crear el almacenamiento al guardar el primero.
- **RF-8.3** Si los datos guardados existen pero no se pueden leer, entonces el sistema deberá mostrar E-10, no modificarlos y terminar con código 1. Se consideran ilegibles cuando:
  - el almacenamiento está vacío (0 bytes);
  - su contenido no se puede interpretar;
  - algún gasto incumple las reglas de esta spec;
  - el sistema no tiene permiso para leerlos.
- **RF-8.4** El sistema deberá ignorar la información adicional que no forme parte de un gasto.
- **RF-8.5** Si no se puede guardar un gasto (sin permiso de escritura, disco lleno), entonces el sistema deberá mostrar E-11, dejar intactos los datos anteriores y terminar con código 1.

### RF-9 Uso incorrecto
- **RF-9.1** Si el usuario ejecuta `gastos` sin comando, usa un comando que no existe, omite argumentos obligatorios, agrega argumentos de más o usa una opción desconocida (un argumento que empieza con `-` y no cumple RF-1.3), entonces el sistema deberá mostrar el mensaje E-12 y terminar con código 2.
- **RF-9.2** El sistema deberá mostrar en español todos los textos de uso y de error, sin ninguna palabra en inglés (ni `usage`, ni `error:` en minúsculas, ni `required`).
- **RF-9.3** Si el usuario interrumpe el programa con Ctrl+C, entonces el sistema deberá mostrar M-3, sin traceback, y terminar con código 130.

### RF-10 Formato de salida y catálogo de mensajes
- **RF-10.1** El sistema deberá mostrar cada monto con el formato `Bs` + espacio + valor con 2 decimales y punto decimal, sin separador de miles. Ejemplos: `Bs 25.50` y `Bs 1000000.00`.
- **RF-10.2** El sistema deberá mostrar cada fecha con el formato `DD/MM/AAAA` (`26/10/2026`).
- **RF-10.3** El sistema deberá usar exactamente estos textos, donde `<…>` se reemplaza por el dato correspondiente:

| Código | Texto |
|---|---|
| M-1 | `Gasto registrado: Bs <monto> en <categoria> el <fecha>.` (con la categoría ya normalizada) |
| M-2 | `No hay gastos registrados en <mes> de <año>.` |
| M-3 | `Operación cancelada.` |
| E-1 | `Error: falta el monto. Ejemplo: gastos agregar 25.50 comida` |
| E-2 | `Error: el monto debe ser mayor que cero.` |
| E-3 | `Error: el monto puede tener como máximo 2 decimales.` |
| E-4 | `Error: "<valor>" no es un monto válido. Usa solo cifras y, si quieres, un punto o una coma con hasta 2 decimales (ej.: 25.50).` |
| E-5 | `Error: el monto máximo por gasto es Bs 1000000.00.` |
| E-6 | `Error: falta la categoría.` |
| E-7 | `Error: la categoría solo puede tener letras, cifras, espacios, "-" y "_", y debe empezar con una letra o una cifra.` |
| E-8 | `Error: la categoría puede tener como máximo 30 caracteres.` |
| E-9 | `Error: la descripción puede tener como máximo 100 caracteres.` |
| E-10 | `Error: no se pudieron leer los datos guardados en <ruta> (<motivo>). No se modificaron. Revísalos o muévelos a otra carpeta para empezar de cero.` |
| E-11 | `Error: no se pudo guardar el gasto (<motivo>). Los datos anteriores no se modificaron.` |
| E-12 | `Error: <motivo en español>.`, seguido del texto de uso, que empieza con `Uso:` |
| E-13 | `Error: la descripción tiene caracteres no permitidos.` |

## 5. Requisitos no funcionales

| Id | Requisito | Cómo se verifica |
|---|---|---|
| RNF-1 Idioma | Todos los textos que ve el usuario están en español (RF-9.2, RF-10.3). | Tests automáticos |
| RNF-2 Exactitud | Los totales coinciden al centavo con la suma manual (`0.10 + 0.20` = `Bs 0.30`). | Tests automáticos |
| RNF-3 Integridad | Si el proceso se interrumpe mientras guarda (Ctrl+C, cierre de la terminal o un error), los datos quedan completos, en su estado anterior o en el nuevo, nunca a medio escribir. Ante un corte de energía, el sistema lo intenta en la medida que lo permita el sistema operativo. | Test automático que simula un fallo mientras se guarda |
| RNF-4 Uso local | La herramienta funciona sin internet y sin servicios externos. | Revisión manual |
| RNF-5 Rendimiento | Cada comando responde en menos de 1 segundo con 10 000 gastos guardados, en el equipo del desarrollador. Con más gastos sigue funcionando, aunque sin garantía de tiempo. | Una prueba manual documentada, fuera de la suite de pytest |
| RNF-6 Consola | Las tildes, la ñ y los emojis se muestran correctamente en PowerShell y cmd (Windows) y en las terminales de Linux y macOS. | Prueba manual en Windows |

## 6. Casos límite

| Entrada o situación | Resultado esperado |
|---|---|
| Monto `""` (vacío) | E-1 |
| Monto `0`, `00`, `0.00` o `0,0` | E-2 |
| Monto `-5` o `-0.001` | E-2 (RF-1.3: `-5` es un valor, no una opción) |
| Monto `25.555`, `0.001` o `1.000` | E-3; `1.000` no se interpreta como mil |
| Monto `+25`, `.50`, `25.`, `1e3`, `NaN`, `1 000`, `25 Bs`, `1.000,50` o `25,5,0` | E-4 |
| Monto `0.01`, `025` o ` 25 ` | Se acepta: `Bs 0.01`, `Bs 25.00` y `Bs 25.00` |
| Monto `1000000` o `1000000.00` | Se acepta: el máximo está incluido |
| Monto `1000000.01` | E-5 |
| Monto inválido y categoría inválida a la vez | Solo el error del monto (RF-2.4) |
| Categoría `"   "` | E-6 |
| Categoría `-ahorro` | E-12: es una opción desconocida (RF-9.1) |
| Categoría `_ahorro`, `comida🍕` o `a/b` | E-7 |
| Categoría `Comida  Rápida` | Se guarda como `comida rápida` |
| Categoría de 30 caracteres / de 31 caracteres | Se acepta / E-8 |
| Categorías `Café` y `cafe` | Son distintas |
| Descripción `"   "` | Se guarda vacía y se lista como `-` |
| Descripción de 100 caracteres con tildes o emojis / de 101 caracteres | Se acepta / E-9 |
| Descripción con un salto de línea interno | Se guarda con un espacio en su lugar |
| Descripción con `\x07` | E-13 |
| Descripción de 101 caracteres que además contiene `\x07` | E-13 (RF-5.4 va antes que RF-5.5) |
| `gastos agregar 25` (falta la categoría) | E-12 |
| `gastos agregar 25 comida almuerzo extra` | E-12 por argumentos de más; una descripción con espacios va entre comillas |
| `gastos` sin comando, o `gastos borrar` | E-12 |
| `gastos agregar --ayuda` | Muestra la ayuda de `agregar` y termina con código 0 |
| Un gasto guardado a las 23:59:59 del último día del mes | Pertenece a ese mes |
| Un gasto de diciembre de 2026 al consultar en enero de 2027 | No aparece |
| Un gasto de octubre de 2025 al consultar en octubre de 2026 | No aparece |
| Un gasto con fecha futura dentro del mes actual (reloj alterado) | Aparece, en su orden de registro |
| Primer uso, sin datos guardados | M-2 en el listado y en el resumen; código 0 |
| Datos guardados vacíos (0 bytes), dañados o con un gasto inválido | E-10; no se modifican |
| Datos sin permiso de escritura, o disco lleno, al agregar | E-11; los datos anteriores quedan intactos |
| Tres categorías empatadas: `ñandú`, `nube` y `árbol` | Se ordenan `árbol`, `nube`, `ñandú` |
| `cafe` y `café` con el mismo total | `cafe` va primero |
| Una sola categoría | Una línea de categoría y la línea `Total` |
| Ctrl+C durante cualquier comando | M-3 y código 130, sin traceback |
| 3 gastos de `1000000` | `Total: Bs 3000000.00` |

## 7. Fuera de alcance (MVP)

- Editar o eliminar gastos ya registrados.
- Registrar un gasto con una fecha distinta a la de hoy.
- Consultar meses anteriores o rangos de fechas.
- Varias monedas: todos los montos están en bolivianos.
- Exportar datos, presupuestos y gráficos.
- Paginar el listado.
- Ejecutar dos comandos al mismo tiempo: si ocurre, no se garantiza el resultado.

## 8. Criterios de finalización

- Cada criterio de aceptación RF-x.y tiene al menos un test automático, y todos los tests pasan.
- Cada caso límite de la sección 6 tiene un test, salvo los que dependen de la consola o de los permisos del sistema, que se prueban a mano.
- Cada RNF se verificó con el método que indica la sección 5.
- Se demostró a mano el flujo completo: agregar varios gastos, listar y ver el resumen.
- No quedan dudas marcadas como [NECESITA ACLARACIÓN].
- El usuario aprobó esta versión de la spec.

## 9. Dudas abiertas

Ninguna. Se resolvieron el 26/10/2026:
- Moneda: `Bs`, una sola moneda (RF-10.1).
- Exportar, presupuestos y gráficos quedan fuera de alcance (sección 7).
- El monto máximo es 1000000 (RF-3.5).
- La fecha se muestra como `DD/MM/AAAA` (RF-10.2).
- Sintaxis posicional (RF-1.1).
- La categoría admite letras, cifras, espacios, `-` y `_`, con un máximo de 30 caracteres (RF-4).
- RNF-5 se verifica a mano.
- Se puede usar un archivo temporal mientras se guarda (constitución, principio 5).
- A1: se ejecuta con `python -m gastos` (RF-1.1).
- A2: los caracteres no imprimibles en la descripción dan E-13 (RF-5.4).
- A3: en un empate que solo difiere en las tildes, va primero la categoría sin tilde (RF-7.3).
- A4: Ctrl+C muestra M-3 y termina con código 130 (RF-9.3).
