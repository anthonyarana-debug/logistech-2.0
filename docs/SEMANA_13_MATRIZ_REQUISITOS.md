# Matriz de Semana 13

Se evalúan los 13 requisitos del profesor con igual peso. Los trece tienen evidencia (100 % de cobertura del bloque del 80 %). La comprobación pública incluye TLS, salud, sesión de administrador y lectura paginada. La calificación corresponde al profesor.

| N.º | Requisito | Estado | Evidencia |
|---:|---|---|---|
| 1 | CRUD funcional | PROBADO | API y Playwright, con integridad y permisos |
| 2 | Paginación y latencia | PROBADO | Páginas y filtros API/UI, página 400 con 10.000 categorías |
| 3 | Múltiples tipos de usuario | PROBADO | Superadmin, administrador, operador asignado y pendiente |
| 4 | Proyecto desplegado en servidor | PROBADO | Lightsail por HTTPS. Landing y API 200, login y consulta paginada verificados desde Internet |
| 5 | PostgreSQL y diagrama | PROBADO | Migraciones y [diagrama editable](MODELO_DATOS.mmd) |
| 6 | CORS restringido | PROBADO | Mismo origen y origen ajeno sin autorización |
| 7 | Pruebas preventivas de caídas | PROBADO | Caídas controladas de PostgreSQL y Gunicorn, vuelta a HTTP 200 |
| 8 | Autenticación y autorización | PROBADO | CSRF, cookies, permisos y aislamiento en API |
| 9 | Inicio de sesión con correo | PROBADO | Acceso por correo y credenciales inválidas en Playwright |
| 10 | Tokens expirados y rutas protegidas | PROBADO | Renovación real y rutas privadas de la aplicación |
| 11 | Pantallas para errores previstos | PROBADO | Validación, 403/404 y ensayos de red, 500 y 503 |
| 12 | Pruebas de 1.000–5.000 | PROBADO | 5.000 GET, 20 VU, p95 39,94 ms y cero errores en el ensayo histórico |
| 13 | Backups | PROBADO | Dump, checksum, cifrado, restauración independiente y persistencia |

Los extras de VPC y optimización se evalúan aparte. La red privada Docker está ensayada. Una VPC de producción se comprobaría con la alternativa EC2. La configuración de carga está acotada y la atribución del pico de p95 requiere medición continua.
