# Constitución — gastos-cli

Proyecto educativo: todo debe poder entenderlo y mantenerlo un desarrollador junior.

1. **Stack mínimo:** Python 3.11+ y solo la biblioteca estándar. La única dependencia permitida es `pytest`, y solo para desarrollo.
2. **La spec manda:** ningún comportamiento se implementa sin una spec aprobada en `docs/specs/`. Si el código y la spec no coinciden, se actualiza primero la spec y luego el código.
3. **Lógica separada de la interfaz:** el módulo de lógica no importa `argparse` ni usa `print` ni `input`. La CLI solo lee argumentos, llama a la lógica y muestra resultados.
4. **Tests primero:** cada tarea empieza con un test que falla. Toda función pública de la lógica tiene al menos un test, y ninguna tarea se cierra si `pytest` no pasa completo.
5. **Persistencia simple:** los datos se guardan en un único archivo JSON local, sin base de datos; mientras se guarda, se permite un archivo temporal para no corromper los datos. Los montos se guardan como enteros en centavos, nunca como `float`.
6. **Todo en español:** nombres, comentarios, mensajes al usuario y documentación van en español. Los identificadores no llevan tildes ni ñ (solo ASCII).
