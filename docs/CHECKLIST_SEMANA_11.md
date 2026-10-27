# Checklist de evaluación — semana 11

Fecha: 27/10/2026. **Preparado para demostración local. Entregable global PARCIAL hasta resolver cloud con el profesor.** No hay entorno público desplegado o verificado. Estados: COMPLETADO = evidencia local aprobada; PARCIAL = parte comprobada; PENDIENTE = sin evidencia suficiente; FALLIDO = comprobación no aprobada.

## Los trece requisitos, uno por uno

| ID | Requisito / estado | Código responsable | Prueba y resultado | Evidencia | Pendiente |
|---|---|---|---|---|---|
| 01 | Cloud preparado/evaluable — **PARCIAL** | Dockerfile target production, requirements-production, production.py, deploy/production.env.example | Imagen Linux/Gunicorn construida, pip check/check-config aprobados; liveness 200 en proxy simulado local, HTTP→HTTPS 301; readiness 503 sin TLS PostgreSQL | fase5-verificacion.json; DESPLIEGUE.md | Cuenta/cuotas, dominio, TLS real, proxy/estáticos, DB privada/CA, limitación compartida, despliegue y verificación externa |
| 02 | Endpoints — **COMPLETADO local** | config/urls.py, accounts/catalog/boxes/core | Health 200, rutas privadas 401; REST positivo/negativo e integración TCP en pytest | ENDPOINTS.md; fase5-verificacion.json; suite 156 | Repetir tras eventual despliegue |
| 03 | Registro/login diferenciados — **COMPLETADO local** | AuthPage.jsx, accounts/views.py | Registro real, confirmación errónea, login válido/inválido, operador pendiente; E2E aprobado | fase5-e2e-final.json | Reservar la ventana de registro antes de exponer |
| 04 | Rate limiting — **COMPLETADO local** | accounts/throttles.py, core/api.py | Tests de ventanas/identidad/IP/rotación/120 por usuario; 429 real de refresh observado en primera regresión | test_throttling.py; test_private_rate_limit_is_per_user_and_recovers; fase5-e2e-inicial.json | LocMem es por proceso; no afirmar límite distribuido |
| 05 | 403/404/en desarrollo — **COMPLETADO local** | Special.jsx, core/views.py | Vistas españolas, navegación E2E; API desconocida 404 JSON | fase5-e2e-final.json; fase5-verificacion.json | Vistas SPA no equivalen a status HTTP del servidor estático |
| 06 | Respuestas HTTP — **COMPLETADO local** | core/errors.py y views/serializers | 200/201/204/400/401/403/404/405/409/429/500, 503 de salud; 500 inyectado solo en prueba, sin detalles internos | test_crud.py, test_auth.py, test_infrastructure.py; fase5-http-integracion.json; fase5-verificacion.json | 500 de interfaz es simulación explícita; no endpoint de fallo en producción |
| 07 | CRUD inicial — **COMPLETADO local** | catalog/boxes, Resources.jsx, BoxDetail.jsx | CRUD permitido, roles, cantidades, FK, empresas cruzadas, estados finales; E2E y PostgreSQL | fase5-e2e-final.json; suite 156 | Productos/empresas/sucursales completos, recepción e historial siguen futuros |
| 08 | Variables de entorno — **COMPLETADO local** | .env.example, configurar_entorno.py, settings, Compose | Config sin expansión pública de secretos; validación de configuración, flags y plantillas | fase5-verificacion.json; test_production_settings.py | Aprovisionar secretos cloud fuera de Git; nunca usar marcadores |
| 09 | Hash de contraseñas — **COMPLETADO local** | accounts/managers.py y validadores Django | Registro comprueba hash distinto al texto y check_password; hashing real | test_registration_hash_and_unassigned_operator; suite 156 | Fixtures de carga sin login usan contraseña inutilizable, no hash débil |
| 10 | Pruebas unitarias — **COMPLETADO local** | backend/tests, frontend/unit | **156 pytest + 5 Node**, más **9 E2E**; sin retries ni protecciones desactivadas | fase5-verificacion.json; fase5-e2e-final.json | Resultados dependen del entorno; no sustituyen validación cloud |
| 11 | PostgreSQL — **COMPLETADO local** | models/migrations, tools/verificar_entrega.py | PostgreSQL real, User 0001, auth_user ausente, migraciones sin pendientes, integridad sin diferencias | fase5-verificacion.json | TLS/restore cloud pendientes; no SQLite |
| 12 | ER editable — **COMPLETADO** | MODELO_DATOS.mmd | Columnas comparadas con los seis modelos, sin diferencias; Mermaid renderizado e inspeccionado | fase5-modelo-datos.svg/.png; fase5-verificacion.json | Tablas de framework/M2M explícitamente omitidas del ER de negocio |
| 13 | Carga 50–100 — **COMPLETADO local delimitado** | load/locustfile.py, run.py, preparar_carga.py | 50 y 100 autenticados activos; 5/10 usuarios/s; 30 s de warmup y ~180 s medidos; 0 fallos HTTP | REPORTE_RENDIMIENTO.md; carga-fase5/resumen-escenarios.csv; fase5-carga-resumen.json | No son navegadores simultáneos ni prueba de 100 logins/s; incidencia CSV cruda documentada |

Balance: **12 completados en su alcance local y 1 parcial (cloud)**. Ningún fallo funcional permanece en la ejecución final aislada. Los tres E2E iniciales fallidos por 429 y el error del escritor CSV se conservan y explican en el informe; no se cambian retrospectivamente por resultados aprobados.

## Antes de la exposición

- [ ] Confirmar con el profesor si una demostración local y preparación documentada satisfacen 01, o exige URL cloud activa.
- [ ] Si exige cloud: acceder a AWS Academy, verificar permisos/EC2/RDS, región, cuotas, presupuesto y autorizar recursos por separado. No enviar credenciales por chat.
- [ ] Ensayar GUIA_DEMOSTRACION.md con las cuentas del archivo local privado. No proyectar archivos .env, cookies, JWT ni contraseñas.
- [ ] Comprobar Docker Linux y servicios saludables; abrir landing, login y estado antes de exponer.
- [ ] Confirmar zoom nativo 200%, lector de pantalla y dispositivo táctil real. CSS zoom 200%, teclado, axe y cuatro anchos ya tienen evidencia automatizada.
- [ ] Evitar ejecuciones repetidas en la misma ventana de rate limit. Esperar Retry-After y explicar 429; no reiniciar servicios para ocultarlo.
- [ ] Tener copia local de informes/CSV/diagrama para consultar evidencia sin depender de Internet.
- [ ] Revisar y aprobar el cierre F5. F6/F7/F8 siguen sin autorización.
