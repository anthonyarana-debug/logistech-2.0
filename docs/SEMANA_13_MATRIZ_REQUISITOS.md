# Matriz de aceptación de Semana 13

La evaluación académica contabiliza requisitos con al menos una evidencia reproducible. Hay 13 de 13 con evidencia local o pública. Esa cifra mide presencia de evidencia y no equivale a la nota. La aceptación operativa exige comprobar en AWS el criterio de la fila. El resultado operativo es 6 de 13 (46,2 %) verificados en AWS, 5 parciales y 2 verificados en ensayo aislado (carga y caídas). Los flujos de QR, recepción e historial se evalúan como criterios adicionales de cierre F7.

| N.º | Requisito | Estado en AWS | Evidencia y límite |
|---:|---|---|---|
| 1 | CRUD completo | PARCIAL | Lectura autenticada en AWS. Escrituras y borrados permitidos probados en el ensayo local |
| 2 | Paginación | PARCIAL | Recuento, límite, orden, filtro e inválidos en AWS. Navegación con varias páginas y aislamiento por rol en ensayo |
| 3 | Tipos de usuario | PARCIAL | SUPERADMIN en AWS. Administrador de empresa y operador en ensayo |
| 4 | Servidor desplegado | PROBADA | DNS público, redirección 308, TLS válido, landing, recursos y ruta React |
| 5 | Base de datos y diagrama | PROBADA | PostgreSQL saludable con volumen persistente y migraciones al día. [Diagrama](MODELO_DATOS.mmd) |
| 6 | CORS | PROBADA | El origen ajeno no recibió Access-Control-Allow-Origin |
| 7 | Prevención de caídas | PROBADA EN ENSAYO | PostgreSQL y Gunicorn recuperaron HTTP 200 tras fallos controlados locales |
| 8 | Autenticación y autorización | PARCIAL | CSRF, cookie, sesión y protección anónima verificados. Permisos completos requieren piloto de roles |
| 9 | Login por correo | PROBADA | Inicio de sesión real del SUPERADMIN por correo en AWS |
| 10 | Tokens expirados y rutas protegidas | PROBADA | Expiración natural en AWS (401), renovación (200), cierre (204) y refresh posterior rechazado (401) |
| 11 | Pantallas para errores | PARCIAL | API 400/401/404 en AWS. Interfaz de recuperación 500/503 y permisos en ensayo |
| 12 | Pruebas de 1.000–5.000 | PROBADA EN ENSAYO | 5.000 GET en k6, 20 VU, p95 39,94 ms y cero errores |
| 13 | Backups | PROBADA | Temporizador activo, checksum de la copia más reciente y evidencia previa de restauración independiente y descifrado externo |

[Resultados de pruebas](SEMANA_13_RESULTADOS_PRUEBAS.md) · [Despliegue y alcance](SEMANA_13_DESPLIEGUE_AWS.md)
