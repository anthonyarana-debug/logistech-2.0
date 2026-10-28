# Comprobaciones — historial y cierre Fase 5

## Adaptación posterior a F5 — idioma y consolidación documental

Nueva base previa: 156 backend aprobadas en 15.33 s sobre PostgreSQL real, antes de cambiar backend. Regresión de adaptación: 163 backend (156 anteriores + siete nuevas), ocho unitarias JS y diez E2E Chromium (nueve anteriores + idioma predeterminado con navegador es-PE); resultado/cifras finales en INFORME_ADAPTACION.md y evidencias/adaptacion-verificacion.json. E2E sin retries, incluida expiración real; no se desactivan límites, CSRF o permisos. Axe y responsive 320/390/768/1440, foco/teclado/Escape y CSS zoom 200% incluidos.

Se conserva la primera regresión ampliada con 162 aprobadas/una fallida por display_name de OPTIONS; corrección a lista de pares para choices DRF, sin cambiar valores de enums. Ver adaptacion-verificacion-inicial.json. No editar F0–F5 para convertirlos en resultados de esta adaptación.

Reproducción aislada, desde la raíz:

```powershell
docker compose -p logistech-language -f docker-compose.yml -f compose.validation.yml up -d --build --wait db
docker compose -p logistech-language -f docker-compose.yml -f compose.validation.yml run --rm --no-deps backend python manage.py migrate --noinput
docker compose -p logistech-language -f docker-compose.yml -f compose.validation.yml up -d --build --wait --wait-timeout 120
.venv/Scripts/python.exe scripts/verify_adaptation.py
```

Preparar datos únicamente en esa base académica nueva (si existen, conservarlos; no repetir creación):

```powershell
docker compose -p logistech-language -f docker-compose.yml -f compose.validation.yml exec -T backend python manage.py create_demo --namespace language-adaptation --output /tmp/language-demo.json
docker compose -p logistech-language -f docker-compose.yml -f compose.validation.yml cp backend:/tmp/language-demo.json .env.language-demo.json
$demoOwner = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls .env.language-demo.json /inheritance:r /grant:r "${demoOwner}:(F)"
$env:PW_BASE_URL='http://127.0.0.1:5174'
$env:PW_DEMO_FILE='../.env.language-demo.json'
$env:PW_EVIDENCE_PREFIX='adaptacion-nueva-ejecucion'
$env:PW_REPORT='../docs/evidencias/local/adaptacion-nueva-ejecucion.json'
Set-Location frontend
npm ci
npx playwright install chromium
npm run test:e2e
Set-Location ..
```

Usar nombres nuevos de evidencia para cada serie; las imágenes y resultados presentes son registros de esta entrega. El resumen E2E saneado está en adaptacion-e2e.json. El script de comprobaciones escribe adaptacion-verificacion.json; para repetir conservando el cierre, copiarlo primero con otro nombre de evidencia. No reiniciar caché para ocultar 429; esperar Retry-After. Ningún comando anterior despliega cloud. Al terminar: `docker compose -p logistech-language -f docker-compose.yml -f compose.validation.yml stop`, conserva volumen y datos. Los puertos 8001/5174 no deben estar ocupados por logistech-f5.

## F5 — registro histórico previo a la adaptación

Antes de modificar: Git limpio en b05ce9e, Docker Linux/servicios, Django/migraciones y **151 pytest aprobadas en 15.73 s**. Lint/build y cinco unitarias JS aprobados. E2E contra el proceso de demostración: **6 aprobados/3 fallidos**, todos por cuota real de refresh consumida previamente (429 y Retry-After ~45 min). No se ocultó la ejecución ni se desactivó el límite.

Entorno aislado `logistech-f5`, puertos temporales loopback 8001/5174, volumen/caché separados y datos DEMO propios: **9/9 E2E aprobados**, incluida expiración real a cinco minutos, mismos controles y dos empresas. Resumen saneado en fase5-e2e-final.json; ejecución inicial en fase5-e2e-inicial.json. Las interceptaciones de fallo de red y de errores 403/500 de interfaz siguen explícitamente simuladas; los casos HTTP TCP/backend se ejecutan realmente. Baseline/migraciones de F1–F4 no se editaron.

Verificador final `python scripts/verificar_fase5.py`: **26 comprobaciones con código 0** en fase5-verificacion.json. Backend **156 passed, 17.05 s** (151 anteriores + cinco políticas de producción), **5 Node**, lint/Ruff/build/npm audit 0 vulnerabilidades, pip check y migraciones sin pendientes. Postgres sin inconsistencias de pertenencia/cantidades ni constraints sin validar; ER de seis entidades sin diferencia de columnas y renderizado SVG/PNG inspeccionado.

Artefacto Gunicorn/Linux: construcción, check-config y dependencias aprobados; contenedor efímero en loopback comprobó 301, liveness 200 con proxy controlado y readiness 503 sin TLS de PostgreSQL. No se presenta como despliegue cloud. check --deploy conserva W005/W021 de HSTS, sin silenciar.

Locust: humo + 50 y 100 usuarios activos reales de API, a 5/10 usuarios/s, warmup 30 s y medida ~180 s. A: 23.19 RPS/p95 22 ms; B: 46.37 RPS/p95 38 ms; sin fallos HTTP. Login masivo no probado: una cuenta HTTP y demás JWT de fixtures. CSV de cierre tuvo incidencia Windows documentada, sin alterar HTTP; exportador corregido y humo posterior aprobado. Ver REPORTE_RENDIMIENTO.md y fase5-carga-resumen.json para las cifras, recursos y límites completos.

UI: alineación 2.0 corregida con posición/baseline explícita, conservando A; revisión manual de landing/login y capturas automatizadas 320/390/768/1440. Axe sin infracciones detectadas en reglas/vistas probadas, Tab/Escape/foco, movimiento reducido y CSS zoom 200%. No certificación WCAG, zoom nativo/lector/tacto físico pendientes. Guion y checklist humano entregados. No carga externa, cloud, pruebas de navegadores adicionales o fases F6–F8.

Las siguientes secciones son registros históricos.

> Registros F1–F3 históricos. El estado actual F4 se documenta en INFORME_FASE_4.md, fase4-verificacion.json y fase4-e2e.json; no interpretar los ocho tests o el esquema vacío de F1 como estado actual.

Fecha: 27 de octubre de 2026 (America/Lima). Windows y contenedores Linux locales. No se ejecutaron pruebas cloud ni de carga.

## Resultados y reproducción

### F4 — estado actual (2026-10-27)

Antes de modificar: Git limpio en `7e9b7b9`, inspección de rutas/modelos/roles/diseño y **146 pytest aprobadas, 14.15 s**, PostgreSQL real. Rama de trabajo `codex/fase-4-frontend`. No se tomó el informe F3 como prueba de funcionamiento.

Backend ampliado: **151 pytest** (146 regresión + cuatro referencias + un procedimiento demo). PostgreSQL test_ creado desde migraciones, sin SQLite. Referencias: roles, empresas cruzadas, productos/sucursales inactivos, categoría incoherente, filtros inválidos, métodos y cache. Demo: claves aleatorias/hash, cantidades esperadas, no sobrescritura y namespace repetido.

Frontend: **5 unitarias Node** de restauración y CSRF, renovación única con 401 concurrentes, refresh rechazado sin bucle, logout concurrente y errores seguros. **9 E2E Chromium** en dos ejecuciones (8 flujos + 1 accesibilidad); resumen saneado `fase4-e2e.json`. Configuración con dos workers, pruebas independientes y sin retries. El caso de expiración espera cinco minutos del servidor; total aproximado seis minutos por la ventana de login. La suite mantiene throttles y puede necesitar esperar ventanas entre ejecuciones, especialmente registro 3/hora e identidad de login 10/15 min.

| Caso E2E | Datos / resultado comprobado |
|---|---|
| Landing, teclado y rutas | CTA, enlace Producto con desplazamiento, 403/404/sesión expirada; movimiento reducido |
| Registro y login incorrecto | POST real, confirmación distinta, operador creado sin empresa; credenciales incorrectas rechazadas |
| Administrador | CRUD categoría; 409 de referencia mostrado; caja creada/editada/eliminada; QR exacto; estado final inmutable; reload/logout reales |
| Operador asignado | Categorías solo lectura; crear caja y rechazarla; sin DELETE |
| Operador pendiente | Aviso y comprobación de asignación; ninguna petición a cajas/categorías/referencias |
| Superadmin | Segunda empresa, seis cajas de base, referencias legibles, menú móvil/Escape |
| Red simulada | Intercepción que aborta API; error y reintento recuperable; explícitamente simulación |
| Expiración real | Access vence a cinco minutos; dos llamadas simultáneas comparten un refresh exitoso; pérdida de cookie + Bearer inválido inyectado lleva a pantalla expirada mediante 401 reales |
| Accesibilidad y errores | Axe sin infracciones detectadas en vistas seleccionadas; CSS zoom 200%; vacío y 403/500 simulados, sin detalles internos |

Responsive automatizado: 320/390/768/1440 px, landing y cajas sin desbordamiento del documento, tabla con scroll local. Capturas verificables en `evidencias/fase4-*.png`. Keyboard automatizado: Tab, foco, Escape en formularios y menú. Ampliación CSS al 200% comprobada; no se confunde con zoom nativo ni con pantalla táctil física.

Revisión manual con navegador integrado: composición de landing y legibilidad, árbol accesible, enlace Producto, vista de login y caída/recuperación real del backend según informe F4. Atajos de zoom no produjeron cambio verificable; pendiente humano. No se ejecutó lector de pantalla, Safari/Firefox, prueba física móvil o medición de campo Web Vitals.

Errores corregidos: reutilización del estado de registro al abrir login; desplazamiento a ancla con React Router; bloqueo de botón durante envío; ayudas de formulario; mensajes españoles ante red caída. El primer pase E2E tuvo dos fallos (texto esperado de 404 incorrecto en prueba y transición registro→login); cinco casos pasaron. Los casos corregidos se volvieron a ejecutar con éxito. Errores de lint (globals del navegador/Node, formato e imports Python) corregidos antes del cierre.

Reproducción: `python scripts/verificar_fase4.py`; desde frontend `npm run test:unit` y `npm run test:e2e` con datos demo del README. No ejecutar E2E contra producción. Evidencias F1–F3 permanecen históricas. Las siguientes secciones de F1 no describen el estado actual.

Ejecutar `python scripts/verificar_fase1.py` con Compose saludable. [fase1-verificacion.json](evidencias/fase1-verificacion.json) conserva comandos, códigos, stdout/stderr y respuestas HTTP. La ejecución final sobre PostgreSQL 17.11 registró **20 comprobaciones con código 0**. Las advertencias no se ocultan: código 0 no significa ausencia de advertencias de producción.

| Comando/comprobación | Resultado real |
|---|---|
| `docker info --format '{{.OSType}} {{.ServerVersion}}'` | `linux 29.5.3` |
| `docker compose config --quiet` | Código 0 |
| `docker compose up -d --build --wait --wait-timeout 180` | Construcción y arranque completados, tres servicios saludables |
| `docker compose ps` | db/backend/frontend saludables; puertos web solo 127.0.0.1 |
| `docker compose exec -T backend python -m pip check` | No broken requirements found; aviso no fatal de caché pip sin permiso de escritura |
| `docker compose exec -T backend python manage.py check` | Sin problemas, 0 silenciados |
| `docker compose exec -T backend python manage.py makemigrations --check --dry-run` | No changes detected |
| `docker compose exec -T backend python manage.py migrate --noinput` | No migrations to apply; auth deshabilitado |
| `docker compose exec -T backend python manage.py showmigrations` | Sin migraciones listadas, código 0 |
| `docker compose exec -T backend python -m tools.verificar_base` | PostgreSQL 17.11, tablas vacías, autenticación no migrada |
| `docker compose exec -T backend python -m pytest --ds=config.settings.testing -q -o cache_dir=/tmp/logistech-pytest-cache` | **8 passed**, 0.77 s en la ejecución final registrada |
| `docker compose exec -T backend ruff check --no-cache .` | All checks passed |
| `docker compose exec -T frontend npm run lint` | Código 0 |
| `docker compose exec -T frontend npm run build` | Build Vite completado |
| `docker compose exec -T backend python manage.py check --deploy --settings=config.settings.production` | Código 0, advertencias HSTS W005 y W021 |
| GET API `/api/v1/health/` | 200 JSON, consulta SELECT 1 real |
| GET API `/api/v1/health/live/` | 200 JSON, sin DB |
| GET API `/api/v1/no-existe/` | 404 JSON en español |
| GET frontend `/` | 200 HTML |
| GET frontend `/api/v1/health/` | 200 JSON mediante proxy |
| Inspección de red sin guardar configuración expandida | PostgreSQL privado, sin host port; frontend/backend en loopback |

También se ejecutaron Ruff sobre backend/scripts y pip check en el venv Windows. npm install inicial y npm ci del contenedor informaron 0 vulnerabilidades en la auditoría npm en ese momento; no equivale a una auditoría completa. No se ejecutó escáner de vulnerabilidades Python/contenedores.

## Ocho pruebas

- Liveness sin consulta DB.
- Readiness ejecuta SELECT 1 con cursor controlado.
- Fallo DB devuelve 503 sin revelar la excepción.
- Ruta API inexistente devuelve JSON 404.
- Auth/admin/sesiones no instalados y motor PostgreSQL configurado.
- Check E001 rechaza habilitar auth.User.
- Simple JWT firma/verifica y rechaza token expirado o con clave ajena en subproceso sin DB.
- Integración PostgreSQL real y readiness 200 en una base de prueba separada.

En Windows se ejecutaron las siete primeras con venv: `7 passed, 1 deselected` al excluir integración. No se utilizó SQLite. El smoke JWT no demuestra registro, login, refresh ni permisos de negocio: son de F2/F3.

## Caída y recuperación

Se detuvo PostgreSQL con `docker compose stop db`. Readiness directo y mediante proxy devolvieron **503**; liveness siguió en **200**. [Evidencia HTTP](evidencias/fase1-caida-postgresql.json). En navegador, «Volver a comprobar» mostró «Servicio no disponible»: [captura real](evidencias/fase1-servicio-no-disponible.png).

Se restauró con `docker compose up -d --wait --wait-timeout 120`, conservando volumen y datos. Tres servicios saludables y web «Entorno conectado» después de volver a comprobar. La ejecución final del verificador se hizo tras la recuperación.

## Interfaz y límites

Revisión en navegador de escritorio de conectado/carga/error. [Captura del entorno conectado](evidencias/fase1-entorno-conectado.png). No se verificó dispositivo móvil real, cámara, accesibilidad completa o flujos de negocio.

No hay migraciones de modelos todavía: migrate/showmigrations solo comprobaron un grafo vacío. No afirmar que se aplicaron migraciones de negocio. Cloud, TLS, backups, carga y roles permanecen sin probar.

## Errores corregidos

| Error inicial | Corrección y repetición |
|---|---|
| Motor Docker inaccesible | docker desktop start; Linux y servicios saludables |
| Congelación de dependencias fallaba por nombre guion/underscore | Consultar importlib.metadata.version; .txt generados, instalación Linux y pip check |
| pytest configuraba Django antes del conftest y faltaba SECRET_KEY | Settings testing separado con valores ficticios; suite aprobada |
| Importación JWT requería auth/contenttypes | Smoke en proceso aislado sin DB; aplicación mantiene auth deshabilitado |
| @eslint/js 10.13.0 inexistente | Consultar registro y fijar 10.0.1, independiente de eslint 10.13.0; instalación/build/lint aprobados |
| Vite EACCES al escribir en /app | Propiedad del directorio para usuario node; mantiene ejecución sin root |
| Ruff no podía escribir caché del contenedor | --no-cache; check aprobado sin ampliar privilegios |
| Formato/imports y salida UTF-8 mal decodificada | Ruff/ESLint y encoding UTF-8 explícito de subprocess |

Pendientes no críticos: W005/W021 (HSTS subdominios/preload) y aviso de caché pip del usuario no root. Los detalles de dominio/producción se resolverán antes de desplegar, sin silenciar advertencias.

## CHECKLIST HUMANO

- Revisar informe y web local; no es necesario repetir manualmente pruebas ya registradas.
- Autorizar F2 para modelos y autenticación.

---

## Fase 2 — Resultados actuales (2026-10-27)

[Evidencia F2](evidencias/fase2-verificacion.json): **14 comandos con código 0**, incluyendo **67 pruebas aprobadas**; duración exacta en la salida pytest del JSON. PostgreSQL 17.11 real; pytest creó base test_ y aplicó el grafo desde cero, sin SQLite. El código de la interfaz frontend no cambió; su build y lint también se verificaron.

Comandos reproducibles desde la raíz: `python scripts/verificar_fase2.py`. Cada comando completo, stdout/stderr y código de salida está en el JSON. Incluye config --quiet, ps, pip check, Django check, makemigrations --check --dry-run, migrate --check, showmigrations, verificar_base, pytest, Ruff, frontend lint/build, check --deploy y smoke HTTP.

### Cobertura relevante

| Objetivo | Pruebas y resultado |
|---|---|
| Registro separado de login | Alta 201, sin tokens; hash PBKDF2 real, operador/company=null |
| Validación y elevación | Email/formato/password/cuerpo inválido y duplicado; nueve combinaciones de campos privilegiados rechazadas sin crear usuarios |
| Login | Email normalizado; válido 200; inválido/ausente/inactivo mismo 401 |
| Endpoints protegidos | me sin token, manipulado, expirado o refresh como access devuelve 401 |
| Sesión | Cookie HttpOnly/path/SameSite/max-age; Secure cuando se activa política production; no-store |
| Refresh/logout | Rotación, rechazo de replay, cierre 204, cookie eliminada e idempotencia; inactividad rechaza access/refresh |
| Concurrencia | Dos conexiones intentan consumir el mismo refresh: una 200 y otra 401, con transacciones PostgreSQL |
| CSRF | Registro/login/refresh/logout sin CSRF 403 JSON; Origin ajeno rechazado aun con token válido |
| Rate limiting | IP login y email entre IP distintas, ventana 15 min, 429/Retry-After y recuperación de ventana; registro, 30 rotaciones refresh y login Admin |
| Modelo y migraciones | User en estado accounts.0001_initial, accounts_user existe/auth_user ausente, flags y email protegidos incluso omitiendo clean |
| Roles iniciales | Superadmin coherente y entrada Admin; staff/administrador de empresa denegados; asignación administrativa validada |
| Tenancy base | Política de empresa activa/objeto propio, sin asignación 403 en vista de prueba no publicada; validaciones de referencias cruzadas |
| Núcleo logístico | UUID independientes, flags frágil/perecedero coexistentes, cantidad/peso válidos, referencias PROTECT y FK inexistente con ValidationError |

Los tests de política y modelo no sustituyen las pruebas de endpoints CRUD de F3, aún inexistentes. No se relajó el hashing, CSRF, throttling o constraints para obtener éxito.

### Migraciones locales

Se ejecutó makemigrations para organizations/accounts/catalog/boxes, se revisó migrate --plan y se aplicó `docker compose run --rm --no-deps --volume "<ruta-backend>:/app" backend python manage.py migrate --noinput`. El usuario propio y su configuración existían antes de la primera aplicación. Todas las migraciones finalizaron OK; la evidencia actual lista las aplicadas y las cuatro fuentes iniciales están versionadas. Se conserva el volumen, sin reset ni reescritura de migraciones.

### Prueba HTTP real

La herramienta `tools.verificar_http_auth` consultó al servidor de Compose por HTTP: me 401, csrf 200, register 201, login 200, me 200, refresh 200, logout 204, refresh posterior 401. No es solamente un test client interno. Usa secretos aleatorios en memoria sin imprimirlos; la cuenta técnica creada queda desactivada, con contraseña inutilizable y sin empresa. Cada ejecución deja una cuenta de prueba rotulada, sin inventario.

### Errores corregidos en F2

- Array/string/número JSON podía producir errores de serializer/throttle: se valida Mapping y se devuelve 400; casos de regresión incluidos.
- La primera prueba de rate limit Admin enviaba POST sin CSRF y recibía 403 antes del throttle. Se corrigió la prueba para enviar CSRF válido y comprobar realmente 429; no se debilitó CSRF.
- Smoke ejecutado en un contenedor auxiliar apuntaba a su propio loopback, sin servidor: se corrigió el destino al alias local backend de Compose; no se publicaron puertos nuevos.
- Referencias ORM inexistentes podían lanzar DoesNotExist durante clean: se conserva el ValidationError de FK de full_clean y se agregó prueba negativa.
- Imports/formato se corrigieron con Ruff; se exceptúan longitudes de línea del código de migraciones generado, no su ejecución ni constraints.

### Diseño y verificaciones no ejecutadas

Se calcularon pares de contraste sRGB en [fase2-contraste.json](evidencias/fase2-contraste.json); esto no certifica accesibilidad de pantallas. Referencias públicas inspeccionadas con navegador y extracción web, con límites detallados en DISENO_UI_UX. SVG originales son composiciones conceptuales, no frontend funcional.

No se ejecutaron carga/Locust, pruebas cloud, Android, móvil real, evaluación completa de accesibilidad, TLS ni backups. El frontend no tiene todavía formularios de autenticación. check --deploy sigue informando W005/W021 sobre HSTS, sin silenciarlas. No hay resultados que inventar para esas verificaciones pendientes.

CHECKLIST HUMANO F2: revisar informe, elegir A/B antes de F4 si se desea y autorizar F3 por separado. Crear superadmin mediante prompt local únicamente si se desea revisar Admin.

---

## Fase 3 — Verificación vigente (2026-10-27)

**146 pruebas aprobadas** en 14.02 s en la ejecución final registrada. De ellas, 67 son la base F2 y 79 los casos CRUD nuevos, con parametrizaciones. PostgreSQL real, hashing F2 intacto y migraciones aplicadas desde cero en DB test_. No SQLite ni pruebas de carga.

Antes de implementar se verificaron Git limpio en e5efee1, servicios saludables, migrate --check, makemigrations --check --dry-run y suite F2: **67 passed en 8.34 s**. Resumen observado en [fase3-base-f2.json](evidencias/fase3-base-f2.json); no se asumió el resultado del informe previo.

[fase3-verificacion.json](evidencias/fase3-verificacion.json) registra **19 comprobaciones con código 0** (15 comandos y cuatro lecturas HTTP). Reproducir con `python scripts/verificar_fase3.py`. Guarda comandos y salidas reales sin secretos; preserva evidencias F1/F2 como históricas.

| Verificación | Resultado |
|---|---|
| Git de inicio | Sin cambios, rama F2 y commit e5efee1; trabajo F3 aislado en codex/fase-3-api-crud |
| Django y dependencias | check sin problemas, pip check sin dependencias rotas |
| Migraciones | Nueva boxes/0002 CHECK status/priority aplicada; migrate --check y makemigrations --check sin pendientes |
| Introspección PostgreSQL | Custom User permanece en 0001, accounts_user existe y auth_user ausente |
| pytest completo | 146 passed; incluye regresión F2, CRUD e integración concurrente/HTTP |
| Ruff backend/scripts y ESLint | Sin errores |
| Build frontend | Correcto, código fuente frontend sin cambios |
| check --deploy production | Solo W005/W021 de HSTS, conservadas y no silenciadas |
| HTTP servidor local principal | Health directo y vía frontend 200; categorías/cajas sin token 401 |

### Casos nuevos de seguridad e integridad

- CRUD positivo con admin/superadmin; lectura/creación/edición de cajas por operador; categorías y DELETE prohibidos al operador.
- Usuario sin empresa denegado en colección y UUID conocido; sin token 401. Empresa inactiva deniega al usuario asignado y no admite escritura global.
- Dos empresas: listados/detalles/PUT/PATCH/DELETE, filtros de empresa/producto/sucursal/categoría/QR/ID, búsqueda y cuerpos con referencias ajenas. La consulta no amplía el ámbito y no modifica filas ajenas.
- Rechazo de mass assignment, campos desconocidos/solo lectura, company incluso propia en cliente no global, created_by e identificadores; superadmin solo elige company explícita al crear.
- FK ajena/inexistente, producto inactivo y relación de categoría incoherente desde SQL externo; datos cruzados no se sirven ni enlazan.
- Cantidades fraccionadas/booleanas/no positivas, pesos inválidos, estados/prioridades no permitidos; CHECK DB probado omitiendo clean.
- Categoría case-insensitive por empresa, duplicados 409, mismo nombre válido en otra empresa; PROTECT y borrados con 204 sin cuerpo o conflicto.
- Lookup autorizado por internal_id y qr_code independientes; colisión regenerada y agotamiento de tres intentos devuelve 409.
- Estados finales sin cambios efectivos/reversión/borrado; reasignación de usuario cambia scope sin cambiar creador histórico.
- Dos conexiones/actores sincronizados: duplicado de categoría da 201/409 y transición opuesta de una caja da 200/409, sin sobrescritura terminal.
- 120 lecturas secuenciales para comprobar el límite privado real, 429/Retry-After, ámbito compartido entre ambos CRUD, separación por usuario y recuperación de ventana. **Es un test de contador, no una prueba de rendimiento/carga.**
- Error 500 inyectado solo en test, JSON seguro incluso con DEBUG de prueba, sin excepción interna en el cuerpo y sin endpoint público de fallo.

### HTTP funcional real sin datos permanentes

`test_crud_over_real_http_in_isolated_postgresql` utiliza live_server de pytest-django y urllib sobre TCP, dentro del contenedor y con DB test_ separada. Ejecutó 15 solicitudes: anónimo 401; categoría POST 201, GET/PUT/PATCH 200 y DELETE 204; caja POST 201, GET/PUT/PATCH 200, DELETE operador 403, detalle ajeno 404, referencia ajena 400, DELETE admin 204 y consulta posterior 404.

Las respuestas/códigos figuran dentro del JSON final. No se publicaron puertos nuevos ni se sembraron fixtures de negocio en la base principal. No se afirma que sea una prueba cloud o una operación manual de usuario en la interfaz. El código del frontend sigue siendo el de F1.

### Migración y errores corregidos

[Salida real de migrate](evidencias/fase3-migraciones.txt): CHECK status/priority aplicado conservando volumen. No se reescribió la migración del User ni se borraron datos para aprobar las pruebas.

Se corrigió una importación de Decimal detectada en lint y al cargar el comando inicial de migración; se repitió y la migración se generó/aplicó correctamente. También se corrigieron formato/imports y una línea larga del verificador. Durante revisión se ajustó la validación del creador para conservarlo tras reasignaciones y se agregaron pruebas; no se ocultaron reglas de pertenencia ni se desactivó seguridad.

### Limitaciones

Rate limiting sigue local/no atómico entre workers. No RLS ni triggers cruzados para impedir todo SQL administrativo directo; la API filtra y valida sus vías. Listas sin paginación inicial, sin endpoints públicos de productos/sucursales, sin recepción/historial completos. Sin carga/Locust, cloud, TLS externo, backups, móvil o pruebas visuales F4. Estas verificaciones corresponden a fases todavía no autorizadas.

CHECKLIST HUMANO F3: revisar informe/contrato y autorizar F4 por separado. Dirección visual ya registrada: A con recursos oscuros de B, sin segundo tema. No se necesita repetir manualmente las comprobaciones técnicas completadas.
