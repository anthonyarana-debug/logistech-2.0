# Decisiones técnicas

## ADR-011 — Cierre de validación local F5

La regresión se ejecuta antes de cambiar código y conserva fallos reales. Para no consumir cuotas/datos de la demostración se usa proyecto Compose separado con límites idénticos, puertos temporales loopback y DB propia; no se presenta su caché nueva como recuperación del proceso previo. Carga 50/100 con identidad autenticada por cuenta, un login HTTP controlado y JWT de fixtures con TTL normal; no prueba login masivo. CSV de cierre corregido sin alterar originales, detalles en REPORTE_RENDIMIENTO.

Producción usa artefacto Linux Gunicorn, verificación de TLS PostgreSQL y proxy confiable opt-in, sin exponerlo. Pruebas locales no acreditan TLS/DB/cloud reales. Resultado global PARCIAL hasta resolver el requisito cloud con el profesor/usuario; no se autorizaron F6–F8. El cambio visual F5 se limita a alinear 2.0 y renovar comprobaciones del sistema A.

## ADR-010 — Integración web F4

React/Fetch sin librería de estado global ni cliente HTTP adicional: access en cierre de módulo, cookie HttpOnly existente, CSRF y promesas compartidas para restauración/renovación. Rutas privadas bloqueadas hasta resolver identidad y pertenencia; autorización definitiva en DRF. Consultas descartadas al cambiar contexto/desmontar; logout con guardia de revisión y marcador no secreto de revocación pendiente.

Un único GET de referencias para formularios mantiene el alcance mínimo autorizado. Empresas/productos/sucursales no ganan CRUD público. Comando explícito crea datos académicos identificados y claves aleatorias fuera de Git, sin modificar el esquema o debilitar constraints.

Dirección A con recursos oscuros de B implementada sin tema alternativo. Tipografías autoalojadas con OFL y SVG propios. Playwright y axe son dependencias de desarrollo; Node test cubre sesión sin otra librería. Trazas desactivadas para no persistir tokens. Validación de zoom CSS se distingue de zoom nativo pendiente; F5/carga/cloud no iniciados. Los ADR y fechas de fases anteriores siguientes son antecedentes.

Fecha: 27 de octubre de 2026. Alcance aplicado: Fase 1. Las decisiones de negocio de ARQUITECTURA.md siguen siendo diseño futuro.

Actualización F2: las decisiones F1 de abajo se conservan como antecedentes. Ya se habilitaron Custom User, modelos y autenticación según los ADR de cierre de este documento; no interpretar la suspensión de auth de F1 como el estado actual.

## ADR-001 — Monolito modular

Aceptado para la configuración inicial mediante autorización del usuario. Django/DRF, React/Vite y PostgreSQL en tres servicios locales. No se agregaron microservicios, colas, Redis, Nginx ni Kubernetes. Apps de negocio se crearán en F2; ahora solo `core` tiene una responsabilidad real: infraestructura y health.

## ADR-002 — Autenticación sin dependencias prematuras

Aceptado y aplicado: auth/admin/sessions/contenttypes no están instaladas en F1. DRF no intenta cargar usuario anónimo del módulo auth. Salud permite acceso público explícitamente y la política por defecto para futuras vistas exige autenticación. Esto no implementa autenticación; JWT aún no está conectado a la API.

No existe una migración inicial de negocio porque no existen modelos. Se ejecutaron `migrate`, `showmigrations` y `makemigrations --check --dry-run`; no hay migraciones que aplicar ni tablas de aplicación. Antes de habilitar autenticación en F2 deben existir `accounts.User`, su configuración AUTH_USER_MODEL y `accounts/0001_initial.py`. El check E001 impide activar auth.User por accidente.

## ADR-003 — Matriz aislada de versiones

Se instaló Python 3.13.17 desde el administrador oficial de Python y se creó `.venv` sin system-site-packages. Docker usa el mismo Python. No se usaron los paquetes Django/DRF globales detectados en F0.

Django 5.2 LTS con parche 5.2.18, DRF 3.16.1 y Simple JWT 5.5.1 se seleccionaron por soporte conjunto, no por coincidir con las versiones globales. Se consultaron metadatos publicados en PyPI: JWT declara Django 5.2 y Python 3.13; la matriz del repositorio incluye Django 5.2/DRF 3.16. La guía estable de JWT tiene una lista anterior y no bastaba como única fuente. La instalación aislada, pip check y smoke de firma/verificación/expiración/firma ajena se ejecutaron en Windows y Linux mediante pytest.

El smoke JWT configura auth/contenttypes únicamente en un subproceso en memoria para importar sus clases: no define endpoints, no migra, no conecta a DB y no cambia INSTALLED_APPS de la aplicación. La autenticación de usuarios reales se validará en F2; estos resultados no la demuestran.

psycopg 3.3.6 usa distribución binaria para evitar compiladores/libpq locales. PostgreSQL se fijó inicialmente en 17.9 y se actualizó a 17.11 tras consultar las etiquetas oficiales de la serie 17; se reutilizó el volumen de la misma versión mayor sin borrarlo. El esquema de aplicación aún está vacío. Todas las comprobaciones finales se repiten sobre 17.11.

React 19.3.1, Vite 8.3.5, Tailwind 4.3.3 y Node 24.19.0 se instalaron con versiones directas exactas y package-lock; `npm ci` funcionó en Linux. ESLint usa @eslint/js 10.0.1 y eslint 10.13.0: sus versiones no coinciden numéricamente. pytest/pytest-django y Ruff se incorporaron para las comprobaciones de esta fase. Locust queda para F5.

Fuentes consultadas:

- [Django 5.2 y compatibilidad Python](https://docs.djangoproject.com/en/5.2/releases/5.2/).
- [Versiones publicadas de Django](https://pypi.org/project/Django/).
- [Metadatos de Simple JWT](https://pypi.org/project/djangorestframework-simplejwt/).
- [Matriz de pruebas de Simple JWT](https://github.com/jazzband/djangorestframework-simplejwt/blob/master/tox.ini) (rama mutable; complementada por pruebas locales).
- [DRF 3.16](https://www.django-rest-framework.org/community/3.16-announcement/).
- [Requisitos Vite](https://vite.dev/guide/).
- [Imagen oficial PostgreSQL](https://hub.docker.com/_/postgres).

## ADR-004 — Secretos, red y configuración

Generar `.env` local con aleatoriedad criptográfica y no sobrescribirlo; plantilla ficticia versionable. Django falla si faltan variables requeridas o se usan marcadores. Producción rechaza DEBUG=true y claves cortas; activa HTTPS redirect y cookies Secure. No se publicaron recursos cloud.

Solo frontend/backend tienen puertos en loopback. PostgreSQL vive en una red `internal` sin host port. Frontend no tiene acceso a esa red. PostgreSQL usa SCRAM para conexiones de red. Los procesos web corren sin root, con capacidades eliminadas y no-new-privileges. El usuario inicial PostgreSQL tiene privilegios locales de administración: crear un rol de aplicación restringido antes de producción. Las variables VITE_ son públicas y solo contienen la ruta API.

No se activa CORS abierto: el navegador usa el proxy de desarrollo en el mismo origen. Producción necesitará definir sitio, proxy y orígenes reales. HSTS de subdominios y preload siguen desactivados hasta conocer el dominio; Django los informa como W005 y W021. No se silencian. Sin proveedor ni dominio no corresponde afirmar seguridad cloud verificada.

## ADR-005 — Usuario, pertenencia y núcleo de datos F2

Aplicado: accounts.User en accounts/0001_initial, email como identidad, UUID y roles explícitos. La configuración intercambiable estuvo activa antes de migrate. Se conservaron grupos/permisos Django, sin conceder negocio global por is_staff. Admin propio solo para SUPERADMIN; procedimientos administrativos para asignar empresa, sin endpoints de asignación públicos.

Company, Branch, Category, Product y Box mínimos sostienen relaciones reales. Categorías privadas por empresa; fragilidad y perecibilidad independientes. Clean/save verifican pertenencia y PostgreSQL impone UNIQUE/CHECK y PROTECT. No hay API CRUD aún ni triggers cruzados; F3 necesita filtros/servicios/permisos. Identificadores independientes generados con UUID y UNIQUE: tratamiento de colisión/reimpresión y consulta REST quedan para fases correspondientes.

## ADR-006 — Sesión web y protección F2

Aplicado: access 5 min en JSON para memoria del cliente; refresh HttpOnly SameSite=Lax, Secure en producción, vigencia de 1 día que se renueva al rotar, path /api/v1/auth/. CSRF en registro/login/refresh/logout; GET csrf para bootstrap. No se implementó un segundo contrato Android que omita CSRF; debe diseñarse con sus fuentes reales.

Refresh usa blacklist y bloqueo transaccional de OutstandingToken para consumo único; prueba concurrente con dos conexiones. Logout invalida el refresh presentado, sin prometer invalidación inmediata del access ya emitido. Desactivar cuenta sí impide access/refresh actuales. Respuestas auth no-store y errores de autenticación genéricos.

Rate limiting DRF local: login IP+identidad, registro/refresh/logout/CSRF por IP; el Admin comparte límite login IP. Se decidió refresh por IP en lugar de la sugerencia inicial por cuenta. Contadores por proceso, sin garantía distribuida o exacta bajo concurrencia. SEGURIDAD.md conserva los límites y pruebas.

## ADR-007 — Diseño documental, sin reconstruir frontend en F2

Industrial Precision con dos alternativas originales A (Hoja de control) y B (Terminal de trazabilidad). Referencias públicas revisadas con límites registrados, pares de color calculados y brief para Stitch. Solo documentos y SVG conceptuales; frontend sin cambios. La elección A/B y el rediseño completo requieren F4 autorizada.

## ADR-008 — CRUD multiempresa inicial F3

Aplicado tras comprobar Git/migraciones/suite F2: ModelViewSet con serializers estrictos, permisos por rol y querysets acotados antes de filtros/lookup. Solo superadmin elige empresa en POST; nunca se transfiere company ni se reasigna created_by por REST. FK se validan en querysets del ámbito y nuevamente bajo transacción/bloqueo; datos relacionados incoherentes externamente se excluyen de lecturas de cajas.

Estados iniciales REGISTERED → RECEIVED/REJECTED, finales sin modificación efectiva ni borrado; DELETE solo REGISTERED administrativo. No se crean eventos Reception. Constraints DB de estados/prioridades en nueva migración, junto a las existentes de unicidad/cantidades. Creador histórico inmutable y válido tras reasignación del usuario. Colisiones de IDs generados se reintentan de forma acotada, sin ignorar otros errores.

Rate CRUD compartido 120/min por usuario, local. Errores inesperados DRF se convierten en 500 JSON sin texto interno; log solo clase. No se añadió dependencia, paginación, CRUD de otros recursos, UI ni pruebas de carga. HTTP funcional real se verifica con servidor efímero de pytest y PostgreSQL test_, sin persistir fixtures de negocio en la base local principal.

## ADR-009 — Dirección visual registrada para F4

Según instrucción expresa del usuario al autorizar F3: A (Hoja de control) como base, recursos oscuros de marca inspirados en B; diseño distintivo, accesible y operativo. No se construye un tema B completo. No se autorizó implementar F4 ni se cambió el frontend durante F3.
