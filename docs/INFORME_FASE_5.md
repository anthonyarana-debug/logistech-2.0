# Informe Fase 5 — validación del entregable del 25 %

Fecha: 27 de octubre de 2026, America/Lima. Rama `codex/fase-5-validacion`, base `b05ce9e` limpia antes de comenzar.

**Validación local COMPLETADA. Entregable global PARCIAL por cloud.** Doce requisitos tienen evidencia local suficiente y uno, cloud, sigue parcial. Se puede realizar una demostración local verificable; si el profesor exige URL pública activa, **todavía no estamos preparados para acreditar ese requisito**. No se creó infraestructura externa ni se iniciaron F6/F7/F8.

## Producto y arquitectura evaluados

LogisTech 2.0 es una plataforma académica de identificación y consulta de mercancía por empresa. El núcleo inicial administra categorías con fragilidad/perecibilidad y cajas con producto, sucursal, cantidad, prioridad, estado, ID interno automático y QR independiente. No incluye inventario avanzado, recepción completa, escaneo/OCR, historial o reportes del 80%.

Arquitectura: monolito modular Django/DRF, React/Vite/JavaScript/Tailwind/Router/Fetch y PostgreSQL privado en Compose. Python 3.13.17, Django 5.2.18, DRF 3.16.1, SimpleJWT 5.5.1, psycopg 3.3.6, PostgreSQL 17.11 y Node 24.19.0; dependencias fijadas. Registro y login separados; JWT access solo en memoria, refresh HttpOnly, CSRF, renovación/expiración/logout reales. SUPERADMIN global; COMPANY_ADMIN solo su empresa; OPERATOR asignado con operaciones permitidas y sin eliminar cajas/administrar categorías. Sin empresa no hay inventarios privados. La autoridad sigue en servidor.

Documentación técnica vigente: [ARQUITECTURA](ARQUITECTURA.md), [BASE_DE_DATOS](BASE_DE_DATOS.md), [ER editable](MODELO_DATOS.mmd), [ENDPOINTS](ENDPOINTS.md), [ROLES_PERMISOS](ROLES_PERMISOS.md), [SEGURIDAD](SEGURIDAD.md) y [DESPLIEGUE](DESPLIEGUE.md). El ER de negocio omite tablas de framework, tal como declara su fuente.

## Auditoría inicial, fallos y correcciones

Se inspeccionaron Git, informe F4, matriz, endpoints, pruebas, plan, configuración y versiones antes de cambiar código. Docker Linux y tres servicios saludables; Django sin problemas y migraciones sin pendientes. Regresión backend: **151 passed, 15.73 s**. Lint/build y cinco unitarias JS aprobados.

Primera regresión E2E en el proceso de demostración: **6 aprobados y 3 fallidos**. Los fallos de reload/restauración/refresh respondían 429 reales con Retry-After de unos 45 minutos, por el presupuesto de refresh acumulado en sesiones anteriores. Se conservó ese resultado; no se borró la caché ni se rebajó el límite para convertirlo en aprobado. Se preparó el proyecto `logistech-f5` con DB, caché y namespace de demostración independientes, mismos límites, y se repitió la suite una sola vez: **9/9 aprobados**, incluida la espera de expiración real de cinco minutos.

Durante una interrupción de la sesión se observaron ambos stacks detenidos con estado Exited(255). Se recuperaron mediante Compose, conservando volúmenes. Los escenarios principales de carga se ejecutaron después de recuperar servicios, sin mezclar ese paro con métricas de capacidad. El primer intento de iniciar A con backend detenido no llegó a generar carga; quedó identificado y se volvió a iniciar cuando el health estaba disponible.

Correcciones dentro de F5:

- `2.0` heredaba desplazamiento de sup: ahora usa posición estática y baseline, sin rediseñar Industrial Precision ni añadir animaciones/librerías UI.
- El arnés E2E acepta URL, datos, prefijo de captura y reporte por entorno; los valores actuales usan nombres F5 para no sobrescribir evidencia F1–F4. Trazas/vídeo/storageState siguen desactivados y los reportes crudos se ignoran.
- Se preparó target Linux production con Gunicorn 26.2.0 y lock complementario; configuración exige PostgreSQL TLS verify-full, orígenes CSRF HTTPS explícitos y proxy confiable opt-in. Cinco pruebas nuevas de política. No se modificaron modelos, migraciones ni reglas CRUD.
- Locust en Windows tuvo error de escritor CSV al cerrar A/B, posterior a la medida. Se conserva; se sustituyó la exportación periódica problemática por CSV síncrono de cierre, historial propio y JSON final oficial. Humo posterior aprobado sin esa excepción. Los datos originales no se reescribieron para ocultarla.

## Resultados finales y trazabilidad

| Verificación | Resultado real |
|---|---|
| Backend | **156 passed, 17.05 s**, PostgreSQL real; hashing y casos cruzados intactos |
| Frontend unitario | **5/5 Node**, restauración/renovación concurrente/logout/errores seguros |
| Navegador | **9/9 Chromium**, dos workers, sin retries; flujos positivos/negativos y cuatro roles |
| Django/migraciones | check aprobado, sin nuevas migraciones ni pendientes; Custom User en 0001, auth_user ausente |
| PostgreSQL | Constraints validados; sin producto/categoría, caja/producto o caja/sucursal cruzados ni cantidades no positivas |
| ER | Columnas de seis modelos comparadas sin diferencias; Mermaid CLI 12.0.0 renderizó SVG/PNG y se inspeccionó la imagen |
| Calidad | Ruff, ESLint, build, pip check y npm audit aprobados (0 vulnerabilidades npm informadas en esa ejecución) |
| Producción local | Imagen Gunicorn construida, check-config y pip check aprobados; 301 y liveness 200 en contenedor efímero/proxy controlado |
| Readiness producción | **503 esperado** sin TLS/CA de la base local: prueba de fallo cerrado; no una conexión cloud verificada |
| check --deploy | W005/W021 de HSTS conservadas, ninguna advertencia silenciada; dominio/subdominios pendientes |

`scripts/verificar_fase5.py` registró **26 comprobaciones con código 0** en [fase5-verificacion.json](evidencias/fase5-verificacion.json). Código 0 no significa ausencia de advertencias ni que el 503 esperado acredite disponibilidad cloud. [E2E inicial](evidencias/fase5-e2e-inicial.json) y [E2E final aislado](evidencias/fase5-e2e-final.json) mantienen resultados distintos y fecha de ejecución, sin payloads secretos.

Cobertura funcional: registro válido y confirmación errónea; login válido/inválido, logout, recarga, renovación única y expiración; usuarios sin asignación; superadmin/administrador/operador; CRUD con integridad, búsqueda por ID/QR y filtros; cantidades/campos prohibidos; cambios de estado y protección terminal; aislamiento de dos empresas; 200/201/204/400/401/403/404/405/409/429/500 y health 503. Los tests HTTP sobre TCP/DB son reales; la inyección de fallo 500 de backend se limita a tests y las interceptaciones de error/red de frontend se declaran simulaciones. No existe endpoint público para forzar fallos.

### Revisión UI y accesibilidad

Se conservaron composición, paleta y componentes de A con recursos oscuros de B. Se revisaron manualmente landing/logo y navegación a login en navegador integrado; la captura [fase5-logo-manual.png](evidencias/fase5-logo-manual.png) muestra la alineación corregida. Landing, dashboard, tablas/formularios, vacíos y errores se comprobaron mediante E2E/axe. Capturas `fase5-landing-*` y `fase5-cajas-*` acreditan 320/390/768/1440 px; scroll de tabla local sin desbordamiento del documento.

Tab, foco visible, Escape, menú móvil y movimiento reducido comprobados. Axe no detectó infracciones en las reglas WCAG A/AA/vistas ejecutadas; CSS zoom 200% con evidencia. Zoom **nativo**, lector de pantalla y tacto físico siguen pendientes humanos; no se afirma certificación WCAG ni pruebas en Safari/Firefox/móviles reales.

## Carga local 50–100

| Escenario | Configurados / activos medidos | Spawn | Warmup | Medición real | Peticiones | RPS | Media | p95 | Fallos HTTP |
|---|---|---|---|---|---|---|---|---|---|
| A | 50 / 50 | 5/s | 30 s | 179.45 s | 4 161 | 23.19 | 14.44 ms | 22 ms | 0 (0.00%) |
| B | 100 / 100 | 10/s | 30 s | 180.44 s | 8 368 | 46.37 | 19.23 ms | 38 ms | 0 (0.00%) |

Cada cuenta verificó identidad en servidor. Una hace login HTTP por escenario; las demás reciben JWT de fixtures con TTL normal para separar capacidad de inventario de la cuota 5/min/IP. **No son 100 logins simultáneos ni 100 navegadores.** Lectura de categorías/cajas, búsqueda y POST/PATCH limitados; dos empresas, máximo una caja nueva y una edición por usuario. Usuarios de carga desactivados al terminar y manifiestos privados eliminados. No se desactivó CSRF, validación, permisos, rate limit o expiración, ni se falsificó IP.

Sin 429/5xx/timeouts de capacidad en A/B. El 429 de regresión inicial se contabiliza aparte. El escritor CSV falló al cerrar con código de proceso 0: snapshot final periódico A/B tenía 18/8 solicitudes menos que el evento de cierre. Se conserva y se explica, sin inventar fallos HTTP o corregir sus números a mano. Consolidado CSV deriva de los eventos finales; humo posterior acredita exportador corregido. Recursos, entorno, errores, datos, límites y reproducción en [REPORTE_RENDIMIENTO](REPORTE_RENDIMIENTO.md), [CSV](evidencias/carga-fase5/resumen-escenarios.csv) y [resumen con recursos](evidencias/fase5-carga-resumen.json).

Las pruebas fueron solo contra runserver/PostgreSQL locales en el mismo equipo que Locust. No prueban máximo de capacidad, infraestructura Gunicorn desplegada, conexiones TLS de cloud, latencias de Internet ni Web Vitals. No se extrapolan a EC2.

## Cumplimiento de trece requisitos

Matriz detallada con código, prueba, resultado, evidencia y pendiente por requisito: [CHECKLIST_SEMANA_11](CHECKLIST_SEMANA_11.md). **02–13 completados en su alcance local; 01 cloud parcial.** No hay requisito declarado FALLIDO en la verificación final local, pero se preservan los fallos iniciales y del exportador. Si la rúbrica exige cloud activo, el 25% permanece incompleto.

Infraestructura: planificada; artefactos preparados parcialmente; **no desplegada y no verificada externamente**. Falta intervención humana para AWS Academy/EC2/RDS, cuotas/costos, dominio/TLS, proxy/estáticos, CA/base privada y limitación compartida antes de publicar. No se compró ni creó servicio externo. Rollback/backup/restore están documentados, no ejecutados en cloud.

## Archivos modificados y entregas

- Backend: Dockerfile/requirements-production, config/settings/production.py; tools/preparar_carga.py, verificar_entrega.py y verificar_wsgi.py; tests/test_production_settings.py.
- Frontend: styles/index.css (alineación 2.0), playwright.config.js, eslint.config.js y e2e/workspace.js/flows.spec.js/accessibility.spec.js (entorno/capturas). Sin nuevos CRUD o librerías de UI.
- Validación: compose.validation.yml y compose.production-check.yml; load/locustfile.py, load/run.py, load-requirements.txt; scripts/verificar_fase5.py y resumir_carga_fase5.py; .gitignore para entorno aislado de carga.
- Documentos: este informe, CHECKLIST_SEMANA_11, GUIA_DEMOSTRACION y REPORTE_RENDIMIENTO; README, matriz, PLAN, ARQUITECTURA, BASE_DE_DATOS, ENDPOINTS, PRUEBAS, SEGURIDAD, DISENO_UI_UX y DESPLIEGUE actualizados; deploy/production.env.example con marcadores ficticios.
- Evidencias F5: verificación y E2E saneados, imágenes responsive/manual, ER SVG/PNG, CSV/HTML/JSON/logs de Locust y muestras de recursos. Las evidencias F1–F4 permanecen intactas en Git.

## Checklist humano y decisión de evaluación

- [ ] Confirmar si el requisito cloud admite preparación local/documental o exige URL activa; si la exige, no presentar 01 como completo.
- [ ] Obtener acceso a AWS Academy y confirmar cuotas/permisos/presupuesto; autorizar por separado recursos, exposición y cualquier costo. Configurar secretos fuera de Git/chat.
- [ ] Revisar DESPLIEGUE: TLS/CA, proxy conocido, PostgreSQL privado, estáticos, HSTS, límites compartidos, backup/restore y rollback antes de cualquier despliegue.
- [ ] Ensayar GUIA_DEMOSTRACION solo con datos DEMO y archivo privado de cuentas; no proyectar credenciales o DevTools de autenticación.
- [ ] Revisar zoom nativo 200%, lector y tacto físico; confirmar legibilidad operativa con el profesor.
- [ ] Revisar informe, CSV originales/consolidado y limitaciones; autorizar el siguiente trabajo expresamente.

Conclusión técnica: núcleo inicial funcional, seguridad local conservada, regresión y carga local demostradas con evidencia reproducible. Preparado para exposición local de los casos verificados; **aprobación académica final condicionada a la rúbrica y al requisito cloud pendiente**. Se detiene F5 para revisión. F6/F7/F8 no comienzan automáticamente.
