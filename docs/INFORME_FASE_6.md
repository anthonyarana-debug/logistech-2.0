# Informe Fase 6 — cierre del primer bloque de administración operativa

Fecha: 28 de octubre de 2026. Rama: `codex/fase-6-administracion`.
Commit de implementación: `a0c5288` (feat(f6): add tenant-scoped operational administration).
Estado: primer bloque implementado y validado localmente. La evolución completa de F6 continúa pendiente en sus siguientes bloques; F7/F8 no iniciadas. No hubo push ni despliegue.

## Recuperación y conservación

Se revisaron status/diff, ramas, commits y PLAN_FASE_6 sin reiniciar el proyecto. La recuperación encontró 31 entradas de estado, frente a los 25 archivos de la referencia anterior: se incluyeron archivos nuevos, no se descartaron. Se mantuvo la rama solicitada y se completó sobre la base d5a1fab. Main y origin/main conservan e7e437c; la internacionalización local y los avances documentales d2a160b/03901ce/02a1207/d5a1fab son ancestros de F6. F0–F5, informes históricos, documentos académicos originales y repositorio Android no se modificaron. No se ejecutaron reset, clean ni eliminación de volúmenes.

Docker Desktop Linux 29.5.3 operativo. Proyecto aislado logistech-f6, PostgreSQL 17.11, volumen logistech-f6_postgres_data; DB sin puerto de host, backend 127.0.0.1:8001 y frontend 127.0.0.1:5174. Se reconstruyeron y verificaron exclusivamente los servicios F6. La base de trabajo no fue migrada ni eliminada. Python y dependencias backend dentro de Docker; Node y dependencias frontend fijadas por el lockfile, unitarias/lint/build también en contenedor. Versiones comprobadas: Django 5.2.18, DRF 3.16.1, SimpleJWT 5.5.1, psycopg 3.3.6 y PyJWT 2.15.1.

## Funcionalidades realmente implementadas

- Empresas: CRUD REST/pantalla para SUPERADMIN; búsqueda, estado, creación/edición, desactivación y borrado protegido por referencias.
- Sucursales y productos: CRUD REST/pantallas por empresa; categorías reutilizan CRUD anterior. SKU normalizado, nombre/SKU únicos por empresa, categoría y referencias de empresa verificadas en servidor.
- Usuarios: listado, creación, edición, asignación de empresa/rol/sucursal y desactivación según permisos. SUPERADMIN administra OPERATOR/COMPANY_ADMIN; COMPANY_ADMIN solo operadores propios. Nadie concede SUPERADMIN/staff/grupos/permisos Django por REST. No se puede reclamar una cuenta pendiente desde COMPANY_ADMIN ni editar otro administrador, root o el propio actor.
- Cuentas desactivadas pierden acceso autenticado; no hay borrado de usuarios. Contraseñas validadas y hasheadas al crear, nunca devueltas; PATCH de password rechazado hasta implementar revocación específica.
- User.branch opcional, misma empresa y activa para nueva asignación. Puede conservarse una asignación inactiva al desactivar una cuenta. Es asignación organizativa: el inventario conserva la autorización empresarial de F3, no una ACL nueva por sucursal.
- Paneles Global operations, Company operations y Operator workspace con recuentos reales; OPERATOR no obtiene directorio/recuento de usuarios. Navegación y acciones por rol, con autorización efectiva en backend.
- Formularios, tablas, búsqueda/filtros, errores, confirmaciones y estados en inglés; diseño Industrial Precision conservado. Responsive sin desbordamiento de página; las tablas anchas mantienen desplazamiento horizontal interno.
- Nuevas rutas /api/v1/companies/, branches/, products/, users/, overview/; contratos y rutas anteriores conservados. DELETE de usuarios: 405. company/created_by/identificadores y privilegios protegidos. Errores seguros, no-store, cuotas y validación estricta reutilizadas.

## Seguridad e integridad

Pruebas con dos empresas cubren consulta/detalle/filtros/cuerpos JSON, referencias ajenas, campos desconocidos/solo lectura, roles protegidos, traslados autorizados y creador histórico. Escrituras releen actor y bloquean filas de actor/destino/empresa/referencias en transacción. Se conserva la protección de borrado y los límites existentes; no se deshabilitaron cuotas para pasar E2E. La ejecución completa esperó una ventana de login real y la caducidad normal de access.

Restricciones DB nuevas: ACTIVE/INACTIVE en Company/Branch/Product y User.branch requiere company. No hay RLS ni triggers que prueben igualdad de empresa entre tablas: esa pertenencia se valida en modelo/servicio, y los querysets excluyen algunas referencias inconsistentes. No usar operaciones SQL/bulk para saltarse validaciones.

Auditoría de secretos sobre índice e historial de todas las ramas, patrones y valores privados locales conocidos: ver evidencias/fase6/secret-audit.json. Incluye comprobación de 20 exclusiones. No se incorporan .env, passwords DEMO, JWT, bases ni volúmenes. Las capturas muestran únicamente datos de prueba y correos example.test; se revisaron visualmente. El análisis por patrones no es certificación absoluta.

## Migraciones aditivas

1. accounts/0002_user_branch_user_user_branch_requires_company.py: FK branch nullable PROTECT y CHECK de company.
2. organizations/0002_branch_branch_status_allowed_and_more.py: CHECK de estados Company/Branch.
3. catalog/0002_product_product_status_allowed.py: CHECK de estados Product.

Las 0001 y Custom User inicial se mantienen; auth_user ausente. Migraciones aplicadas y sin pendientes solo en F6 aislado. Una prueba PostgreSQL migra desde 0001 con datos históricos y comprueba conservación de UUID, internal_id, QR, creador, referencias y cantidad. Antes de migrar otra base se requiere backup/restauración y revisión de datos inválidos; no se hizo ese cambio en la base de trabajo.

## Resultados reales de verificación

| Verificación final | Resultado | Evidencia |
|---|---|---|
| pytest completo con PostgreSQL real | 216 passed in 19.00s; 163 previas + 53 nuevas | evidencias/fase6/checks.json |
| Unitarias frontend (Node test runner) | 12 pass, 0 fail; descubrimiento confirmado | checks.json |
| Playwright completo, 1 worker, 0 retries | 13 passed, 0 fallos/omitidas/flaky; 375.66 s | e2e-complete.json |
| Accesibilidad y responsive | axe sin violaciones en escenarios comprobados; 320/390/768/1440 y ampliación CSS 200 % | Playwright y PNG |
| Inglés predeterminado | Catálogo de claves literal y navegador con preferencias españolas pasan | Unitarias y E2E language |
| Django check | Sin problemas | checks.json |
| migrate --check / makemigrations --check --dry-run | Sin pendientes / No changes detected | checks.json |
| Introspección PostgreSQL | Custom User en 0001, auth_user ausente, versiones y tablas reales | checks.json |
| Ruff backend / pip check | Pasan / sin dependencias rotas | checks.json |
| ESLint / Vite build | Pasan; 42 módulos, build 273 ms | checks.json |
| Ruff de scripts/verify_f6.py / git diff --check | Pasan | ejecución de cierre |

La cifra 203 previa no se adoptó como validación final. Se conservaron resultados intermedios 205 en checks-pre-resume.json y fallos E2E iniciales (1 correcto, 2 fallidos) en e2e-operations-initial.json. Tras correcciones, 3 E2E nuevas pasaron en resume-e2e-operations.json y luego se ejecutó la suite completa de 13. Los reportes JSON publicados son resúmenes sin passwords, adjuntos privados ni contextos de error.

Regresión comprobada: registro/login/logout/refresh/caducidad, categorías y cajas, scopes global/empresa/operador pendiente, estados, cantidades, referencias, errores 403/500 y fallo de red. Estados REGISTERED/RECEIVED/REJECTED y QR independiente conservan su significado. No se repitió Locust, no se ejecutó k6 y no se atribuyen las métricas F5 a los endpoints F6.

## Errores corregidos

- Faltaba la clave inglesa last_name y el formulario de usuario global fallaba al renderizar: se añadió y se cubrió el catálogo completo de referencias literales.
- .dockerignore excluía unit/: se incluyó y el verificador exige descubrimiento de pruebas mayor que cero.
- La desactivación conservando sucursal inactiva era rechazada: se admite la referencia actual, manteniendo prohibidas nuevas asignaciones inactivas. Se conserva también la empresa inactiva en el formulario de cuenta existente para poder desactivarla.
- Selectores ambiguos Status/Role en E2E se limitaron al diálogo, sin alterar el producto para acomodar pruebas.
- El verificador nuevo tenía una línea que excedía Ruff: corregida y comprobada.
- La salida de inspección Python no admitió un símbolo Unicode en la consola Windows; fue un error del volcado diagnóstico, no de tests. Se consultaron los reportes UTF-8 sin modificar resultados.

## Archivos de implementación y pruebas

- `backend/apps/accounts/migrations/0002_user_branch_user_user_branch_requires_company.py`
- `backend/apps/accounts/models.py`
- `backend/apps/accounts/operations.py`
- `backend/apps/accounts/serializers.py`
- `backend/apps/catalog/migrations/0002_product_product_status_allowed.py`
- `backend/apps/catalog/models.py`
- `backend/apps/catalog/serializers.py`
- `backend/apps/catalog/views.py`
- `backend/apps/core/operational_serializers.py`
- `backend/apps/core/operations_messages.py`
- `backend/apps/core/overview.py`
- `backend/apps/organizations/migrations/0002_branch_branch_status_allowed_and_more.py`
- `backend/apps/organizations/models.py`
- `backend/apps/organizations/serializers.py`
- `backend/apps/organizations/views.py`
- `backend/config/urls.py`
- `backend/tests/test_f6_migrations.py`
- `backend/tests/test_operations.py`
- `frontend/.dockerignore`
- `frontend/e2e/operations.spec.js`
- `frontend/src/components/AppShell.jsx`
- `frontend/src/components/ui.jsx`
- `frontend/src/i18n/en.js`
- `frontend/src/main.jsx`
- `frontend/src/pages/Administration.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/services/operations.js`
- `frontend/unit/operations.test.js`
- `scripts/verify_f6.py`

Documentación actualizada: README, ARQUITECTURA, ENDPOINTS, API_INTERNA, BASE_DE_DATOS, MODELO_DATOS.mmd, ROLES_PERMISOS, SEGURIDAD, DECISIONES_TECNICAS, MATRIZ_ENTREGABLES, PLAN y PRUEBAS. Nuevos PLAN_FASE_6, CLOUD_FASE_6, este informe y evidencias/fase6. Los informes históricos y documentos académicos se conservan sin cambios. Inventario de evidencias y hashes en evidencias/fase6/manifest.json.

## Revisión visual y evidencias

Se inspeccionaron capturas reales de Companies global, Branches/Products/Users de administrador, Users a 390 px y dashboard de operador ya cargado. Se conservan también capturas reales de regresión landing/cajas y ampliación CSS. Los nombres españoles de productos/sucursales de prueba son datos introducidos, no textos traducibles de la interfaz. El helper anterior usó rutas relativas desde la raíz: se recuperaron sus PNG originales desde el directorio hermano a evidencias/fase6, sin redibujar ni inventar imágenes. Para repetir, ejecutar Playwright desde frontend/ como indica PRUEBAS.md.

## Límites y siguiente bloque

Pendientes: QR gráfico/escáner y resolución segura; recepción transaccional/idempotente; movimientos, saldos/conciliación, auditoría persistente, estadísticas históricas/reportes y Android. No hay stock calculado ni historial auditable completo. No se analizó ni modificó el repositorio Android en este bloque; la compatibilidad debe revisarse antes de integrarlo.

El siguiente bloque propuesto es identificación QR y diseño del registro auditable de recepción, conservando estados actuales hasta introducir el modelo y sus migraciones. PLAN_FASE_6 detalla la secuencia. Para producción faltan paginación, cuotas distribuidas, backup/restauración real del entorno objetivo y verificación cloud. CLOUD_FASE_6 prepara esa ruta sin aprovisionamiento, publicación ni costes.

## Checklist humano y estado de entrega

- [x] Primer bloque implementado, regresión y seguridad comprobadas en entorno aislado.
- [x] Rama solicitada, historial, cambios locales, F0–F5 e internacionalización conservados.
- [x] Commits locales identificables; main estable sin modificar, sin push ni despliegue.
- [ ] Revisar pantallas con SUPERADMIN, COMPANY_ADMIN y OPERATOR; usar credenciales privadas locales.
- [ ] Revisar políticas de asignación/desactivación, campos protegidos y límites de este bloque.
- [ ] Programar backup/restauración y migración controlada de otra base antes de usar el esquema F6 allí.
- [ ] Revisar entrega antes de integrar en main o publicar; no se hizo ninguna de estas acciones.
- [ ] Definir reglas de recepción/trazabilidad y compatibilidad móvil antes del siguiente bloque.

El estado y SHA del commit documental final se entregan con git status/log al cierre; este informe identifica el commit de código probado para evitar una referencia circular al commit que contiene el propio informe.
