# Informe de pruebas y validación

**Estudiante:** Ermis Sotomayor  
**Proyecto:** Alke Wallet, módulo 7  
**Fecha:** 30 de septiembre de 2026

## Resultado

**20 pruebas aprobadas, 0 fallos, 0 errores.** Ejecución final: 16,178 segundos. La suite creó una base SQLite temporal, aplicó todas las migraciones y destruyó la base de prueba al terminar. La salida completa se conserva en `resultados_pruebas.txt`.

Entorno de validación: Windows, Python 3.12, Django 4.2.30 y SQLite. Se verificaron además la interfaz web con sesión real y la administración. No se utilizó dinero ni información bancaria real.

| N.º | Escenario | Resultado observado |
|---|---|---|
| 1 | Depósito y retiro con decimales | 100,25 - 10,10 = 90,15 exactos |
| 2 | Transferencia | Origen 64,80; destino 35,20; total conservado |
| 3 | Saldo insuficiente | Rechazo sin crear movimiento |
| 4 | Destino excede límite de saldo | Reversión completa; origen conserva 100 |
| 5 | Montos inválidos | Rechaza cero, negativo, tres decimales, NaN, infinito, texto y exceso de dígitos |
| 6 | Destinos inválidos | Rechaza destino ausente, propia cuenta e inexistente |
| 7 | Operación sobre cuenta ajena | Rechazo del servicio |
| 8 | CRUD de cuenta | Crear, consultar, editar y borrar; saldo no editable por POST |
| 9 | Acceso a cuentas ajenas | GET y POST reciben 404 |
| 10 | Eliminación de cuenta con historial | Se conserva aunque su saldo sea cero |
| 11 | Formulario sin CSRF | HTTP 403 |
| 12 | Acceso anónimo | Redirección al inicio de sesión |
| 13 | Registro y perfil | Creación, edición y eliminación de perfil sin cuentas y usuario |
| 14 | Relaciones y consultas | Uno a uno, contactos, conteos ORM y raw correctos |
| 15 | Restricciones SQL | Rechaza saldo negativo y movimiento de monto cero |
| 16 | Páginas y CSV | HTTP 200, encabezados CSV y descarga correctos |
| 17 | Formulario de transferencia y filtro | Movimiento creado y filtro devuelve una transferencia |
| 18 | Privacidad e historial del receptor | No ve operaciones ajenas; sí su transferencia recibida |
| 19 | Administración y logout | Permisos staff y cierre de sesión POST; GET rechazado |
| 20 | Perfil ajeno | Edición y eliminación reciben 404 |

## Comprobaciones adicionales

- `manage.py check`: sin incidencias.
- `makemigrations --check --dry-run`: no se detectaron cambios pendientes.
- `showmigrations gestion`: ambas migraciones aplicadas.
- `collectstatic --noinput`: 126 archivos estáticos recopilados correctamente.
- Inicio de sesión en navegador: usuario `ermis`; resumen con $235.000, dos cuentas y tres movimientos de ejemplo.
- Reportes: principal $175.000, ahorros $60.000; tres tipos de operaciones y consulta SQL de cuentas con saldo positivo.
- Administración: clientes, cuentas y transacciones visibles para el superusuario.
- Diseño revisado en vista angosta y de escritorio. Evidencias PNG en `capturas/`.

## Alcance y límites

El resultado valida los casos indicados en entorno local. No certifica concurrencia bajo carga, ejecución en PostgreSQL, despliegue público, integración bancaria ni entrega en GitHub. La configuración PostgreSQL está preparada; su validación requiere un servidor real. Django 4.2 se conserva por la versión didáctica de la consigna y debe actualizarse antes de un uso público.

El sistema conserva los movimientos confirmados y restringe las eliminaciones para mantener la integridad. El CRUD completo se demuestra con cuentas vacías y perfiles nuevos. Las pruebas no escriben sobre los datos del usuario.

## Conclusión

Los casos ejecutados validan las funciones centrales solicitadas: autenticación, CRUD, relaciones del ORM, migraciones, consultas, administración y protección de saldos. El prototipo es reproducible mediante las instrucciones del README y el comando de datos de demostración.
