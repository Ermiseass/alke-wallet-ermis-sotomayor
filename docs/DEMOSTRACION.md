# Demostración funcional

**Ermis Sotomayor · Alke Wallet · Módulo 7**

La aplicación ejecutable es el prototipo solicitado. La consigna permite entregar un prototipo **o** un video; no se ha generado un video en esta entrega.

## Recorrido sugerido (5 a 7 minutos)

1. Ejecutar `INICIAR.bat`. Elegir contraseña local e ingresar con `ermis`.
2. Mostrar el resumen: saldo total inicial $235.000; cuenta principal $175.000 y ahorros $60.000. Los datos son ficticios.
3. Abrir **Mis cuentas**. Crear una cuenta llamada “Prueba CRUD”, abrir su detalle, cambiar el alias a “Cuenta de prueba” y eliminarla vacía. Confirmar que desaparece.
4. Abrir **Mi perfil**, cambiar el teléfono y seleccionar un contacto. Explicar que usuario-perfil es uno a uno, cliente-cuentas uno a muchos y contactos muchos a muchos.
5. En **Nueva operación**, depositar $1.000 en Cuenta principal. Luego retirar $200. El saldo de esa cuenta debe quedar en $175.800.
6. Abrir el detalle de Mis ahorros, copiar su UUID. Transferir $500 desde Cuenta principal hacia ese UUID. Resultado: principal $175.300, ahorros $60.500, total $235.800.
7. Intentar retirar $999.999. Mostrar el mensaje de saldo insuficiente y comprobar que el saldo no cambia.
8. Abrir **Movimientos**, filtrar transferencias. Abrir **Reportes** y descargar el CSV. Explicar que se usan agregaciones ORM y una consulta raw con parámetros.
9. Entrar a **Administración**. Mostrar clientes, cuentas y transacciones; los movimientos confirmados se consultan pero no se editan ni eliminan.
10. En la terminal de Visual Studio Code, ejecutar `python manage.py test gestion --verbosity 2` dentro del entorno activado. Mostrar el resultado OK.

Los importes de los pasos 5 a 7 presuponen una demo recién creada y que cada operación se ejecuta una sola vez. Una nueva ejecución de `demo` no reinicia los datos.

## Evidencias incluidas

- `capturas/01_resumen.png`: cuentas, saldo y movimientos iniciales.
- `capturas/02_operacion.png`: formulario de operaciones.
- `capturas/03_reportes.png`: agregaciones y consulta SQL.
- `capturas/04_admin.png`: aplicaciones y modelos en administración.
- `resultados_pruebas.txt`: ejecución real de la suite.
- `verificacion.txt`: comprobaciones del sistema y migraciones.

Si el profesor exige específicamente capturas de Visual Studio Code, abrir `settings.py`, `models.py` y `migrations/` y capturar también la terminal con `showmigrations` y los resultados de shell. Las capturas incluidas en esta entrega corresponden al navegador, no al editor.
