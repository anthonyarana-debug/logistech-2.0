# Auditoría inicial — LogisTech 2.0

Fecha: 26 de octubre de 2026 (America/Lima). Alcance: FASE 0, exclusivamente auditoría y planificación.

## Resultado

Repositorio inicial sin aplicación. Es posible diseñar el sistema, pero no verificar el Android original, su API ni una infraestructura cloud. No se implementaron frontend, backend, modelos ni servicios. Las propuestas de estos documentos no son funcionalidades terminadas.

## Evidencia local

| Comprobación ejecutada | Resultado observado |
|---|---|
| `Get-ChildItem -Force` | Solo `.git` antes de esta documentación |
| `git status --short` y `git status --porcelain=v1` | Sin cambios al iniciar |
| `git log -5 --oneline` | Error esperado: `master` todavía no tiene commits |
| `git ls-files` | Sin archivos versionados |
| `git remote -v` | Sin remotos configurados |
| `git branch --show-current` | `master` |
| `git rev-parse --show-toplevel` | Directorio de trabajo indicado por el usuario |
| Búsqueda de `AGENTS.md` en el directorio y sus ancestros | Ninguno encontrado |
| `git --version` | 2.54.0.windows.1 |
| `python --version` | 3.14.5 |
| `node --version` / `npm --version` | v24.19.0 / 11.17.0 |
| `docker --version` / `docker compose version` | 29.5.3 / v5.1.4 |
| `docker info --format '{{.ServerVersion}}'` | Falló: no existe el canal `dockerDesktopLinuxEngine`; motor Linux no accesible |
| `Get-Command psql, pg_isready` mediante comprobación individual | No disponibles en PATH; no prueba que PostgreSQL esté ausente del equipo |
| `python -m pip --version` | 26.1.1, instalación global Python 3.14 |
| `python -m pip show ...` | Django 6.0.5 y DRF 3.17.1 instalados globalmente |
| Misma consulta de paquetes | Simple JWT, psycopg, pytest, pytest-django y Locust no encontrados en ese intérprete |
| `python -m venv --help` | Disponible; no se creó entorno ni se instaló software |

No se conectó a PostgreSQL, no se ejecutaron migraciones, pruebas funcionales ni carga. No se inspeccionaron archivos privados fuera del alcance para buscar el proyecto anterior. No se consultó ni probó el VPS antiguo.

## Proyecto anterior y contrato

No se encontraron Kotlin, Gradle, Compose, CameraX, ML Kit ni Retrofit en este repositorio. Las tecnologías y rutas del texto del usuario son referencias sin corroborar. No existe código local reutilizable identificado. Se conservarán como conceptos la identificación alternativa, los estados y la recepción; la reutilización de código queda pendiente de revisar fuentes reales.

| Referencia proporcionada | Propuesta nueva, todavía no implementada | Etapa |
|---|---|---|
| `POST /login` | `POST /api/v1/auth/login/`, email y contraseña; contrato JWT por documentar | F2 |
| Sin ruta de registro confirmada | `POST /api/v1/auth/register/`, operador sin empresa | F2 |
| `/registrarCaja`, `/cajas/todas` | Colección REST `/api/v1/boxes/` | F3 |
| `/caja/{qr}` | Consulta filtrada autorizada por `qr_code` o `internal_id`; detalle por UUID | F3 |
| `PUT /cambiarEstado` | Actualización validada del detalle; transición avanzada pendiente | F3/F6 |
| `/tipos_caja` | No equivale automáticamente a categoría de producto; pendiente de fuentes | F6 |
| `/ubicaciones/disponibles`, `/ubicaciones` | Ubicación de almacén distinta de sucursal; pendiente de diseño operativo | F6 |
| `/historial/todos` | Historial restringido por empresa, sin ruta comprometida aún | F6 |
| `/reporte/general?periodo=` | Reportes por rol y empresa | F6 |
| `/ws/{userId}` | Diferido; sin WebSocket para el 25 % | F6 o posterior |

No se garantiza compatibilidad directa con Retrofit. La integración Android requerirá comparar autenticación, nombres, tipos, errores, estados y paginación con el código real. No se crearán alias de compatibilidad sin esa revisión.

## Riesgos y decisiones pendientes

| Riesgo | Impacto | Tratamiento propuesto |
|---|---|---|
| Motor Docker no accesible | Impide validar Compose y PostgreSQL | Iniciar Docker Desktop con motor Linux y repetir diagnóstico en F1 |
| Dependencias globales sin matriz conjunta verificada | Instalación no reproducible o JWT incompatible | Entorno aislado; seleccionar versiones mantenidas y probarlas en F1/F2 |
| Código original ausente | Contrato heredado desconocido | Continuar API propia, sin declarar compatibilidad |
| Cambio tardío del usuario de Django | Migraciones difíciles de corregir | No migrar autenticación por defecto en F1; usuario propio en primera migración de F2 |
| Fuga entre empresas | Exposición de inventario | Filtro por empresa en colecciones, detalle y referencias recibidas; pruebas con dos empresas |
| Registro manipulable | Elevación de privilegios | Rechazar campos de rol, empresa y flags administrativos |
| Mezclar catálogo global y privado | Permisos ambiguos | Categorías privadas por empresa, política explícita propuesta |
| Duplicar datos de caja/producto/empresa | Relaciones incoherentes | Validar pertenencia y proteger relaciones; ver arquitectura |
| Identificador `CJ-####` | Agotamiento/colisiones | UUID independiente con prefijo y restricción UNIQUE |
| Throttle en memoria | Contadores por proceso, carreras | Limitar afirmaciones locales y diseñar solución compartida antes de varios workers |
| Cuenta cloud/cuotas/rúbrica no disponibles | Entorno externo no evaluado | Preparación documental en F5; despliegue requiere autorización |

La documentación estable de Simple JWT consultada enumera versiones anteriores a las instaladas; esto es una brecha de evidencia, no prueba de incompatibilidad. No se recomienda degradar automáticamente a versiones fuera de soporte para coincidir con esa lista. La combinación definitiva queda pendiente de metadatos actuales y pruebas aisladas.

## CHECKLIST HUMANO

- Autorizar la FASE 1 después de revisar estos documentos.
- Iniciar Docker Desktop y habilitar el motor Linux para verificar la infraestructura local en F1.
- Si está disponible, indicar la ubicación o adjuntar el proyecto Android original; no bloquea la base web independiente.
- Antes de F5, confirmar rúbrica, fecha de entrega y entorno cloud académico disponible. Nunca compartir secretos en el chat.

## Fuentes técnicas consultadas

- [Django: usuario personalizado y migraciones](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/).
- [Simple JWT: requisitos publicados](https://django-rest-framework-simplejwt.readthedocs.io/en/stable/getting_started.html).
- [DRF: límites y concurrencia del throttling](https://www.django-rest-framework.org/api-guide/throttling/).
- [Vite: requisitos del entorno](https://vite.dev/guide/).

Las versiones locales se obtuvieron de comandos, no de estas páginas. No se fijaron versiones del proyecto durante esta fase.
