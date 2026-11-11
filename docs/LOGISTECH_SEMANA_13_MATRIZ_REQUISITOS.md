# Matriz de requisitos de LogisTech 2.0 para Semana 13

La guía presenta hitos de 80 % y 100 %. La semana 13 no fija por sí sola cuál de los dos debe calificarse. El respaldo inicial fue `9b840a0ac28df6e8d0f3530571aed0ee1b1ad046`.

| Requisito | Implementado | Incompleto | No implementado | Evidencia | Acción |
|---|---|---|---|---|---|
| 80 % · CRUD | Sí | — | — | pytest y Playwright. Empresas, sucursales, usuarios, categorías, productos y cajas según rol | Mostrar alta, consulta y edición. Borrado sujeto a referencias y estado |
| 80 % · Paginación | Sí | Rendimiento a gran escala | — | Nueve casos API, navegación E2E y k6 GET | Medir filtros y páginas profundas con cardinalidad representativa |
| 80 % · Roles y aislamiento | Sí | — | — | SUPERADMIN, COMPANY_ADMIN, OPERATOR y operador sin asignación en las suites | Mostrar diferencias desde cuentas de ensayo |
| 80 % · Servidor desplegado | Ensayo Gunicorn y Caddy local | Despliegue público | — | HTTPS en localhost:8453 | Autorizar y ejecutar la guía AWS |
| 80 % · PostgreSQL y diagrama | Sí | — | — | Migraciones, restauración y MODELO_DATOS.mmd editable | Mostrar los modelos y restricciones |
| 80 % · CORS | Sí | — | — | React y API en el mismo origen. Respuesta a origen externo sin cabecera de autorización | Verificar de nuevo después de publicar |
| 80 % · Prevención de fallos | Sí | Validación cloud | — | Checks, pruebas, límites Docker y restauración | Configurar vigilancia en el servidor aprobado |
| 80 % · Autenticación y correo | Sí | — | — | Registro, login con correo, CSRF y JWT | Mostrar login y renovación |
| 80 % · Tokens expirados y rutas | Sí | — | — | Expiración real E2E y autorización API | Mostrar ruta protegida en sesión privada |
| 80 % · Pantallas de error | Sí | — | — | Componentes React y errores 401, 403, 404 y 429 | Mostrar error controlado local |
| 80 % · Carga 1000–5000 | Seis escenarios acotados | Capacidad y ejecución representativa | — | 100 GET en el perfil mayor ejecutado. Evidencia CSV/JSON | Caracterizar duración, datos y cuotas antes de ampliar |
| 80 % · Backups y recuperación | Sí | Ensayo cloud | — | Dump, checksum, restauración independiente y reinicio | Programar copias fuera de la máquina cloud cuando exista |
| 100 % · Flujo funcional | Núcleo, QR, recepción e historial | Validación integral de operación externa | — | Suites F6/F7 y Semana 13 | Ejecutar piloto y cerrar pendientes |
| 100 % · Carga 10000–50000 | Parámetros de iteraciones preparados | Capacidad, presupuesto de cuota y tiempos | — | Runner limitado a 20 VU y dos minutos | Diseñar y autorizar una ejecución con capacidad suficiente |
| 100 % · Cuellos de botella | Muestras p90/p95/p99 y recursos puntuales | Curva con cardinalidad y concurrencia creciente | — | Informe k6. Límites de registro y API conservados | Analizar consultas y snapshots bajo carga sostenida |
| 100 % · Logs y recuperación | Acceso JSON de Gunicorn y Caddy, errores React, rollback documentado | Alertas y operación cloud | — | Docker, captura y recuperación local | Ensayar alertas en entorno autorizado |
| Extras · VPC, CI/CD y migración | Red interna Docker, CI de seguridad existente y restauración lógica | Automatización de release | VPC propia | Workflow production-security y ensayos F7 | Evaluar red privada cloud y pipeline tras autorización |
