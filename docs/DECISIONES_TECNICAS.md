# Decisiones técnicas

Fecha: 27 de octubre de 2026. Alcance aplicado: Fase 1. Las decisiones de negocio de ARQUITECTURA.md siguen siendo diseño futuro.

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
