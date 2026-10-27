# Informe de cierre — Fase 3

Fecha: 27 de octubre de 2026 (America/Lima).

FASE COMPLETADA: API REST y CRUD inicial de categorías y cajas.

ESTADO: **Completa en el alcance autorizado de F3.** F4/F5 no iniciadas. El 25 % sigue pendiente de frontend funcional y validación final; no se declara entrega cloud ni pruebas de carga.

## VERIFICACIÓN PREVIA

Antes de escribir la implementación se comprobó Git limpio en `e5efee1`, rama F2, tres servicios saludables, migrate --check con código 0 y makemigrations --check --dry-run sin cambios. La suite F2 volvió a ejecutarse: **67 passed en 8.34 s**. Resumen observado en [fase3-base-f2.json](evidencias/fase3-base-f2.json). Trabajo aislado en `codex/fase-3-api-crud`.

## FUNCIONALIDADES

- CRUD `/api/v1/categories/` y `/api/v1/boxes/`, detalle por UUID, GET/POST/PUT/PATCH/DELETE y errores JSON.
- JWT obligatorio; superadmin global, administrador solo de su empresa, operador asignado con lectura de categorías y creación/edición de cajas; sin administración de categorías ni DELETE. Usuario sin empresa no accede a recursos privados.
- Aislamiento en querysets, detalle y filtros; FK de la misma empresa y activas; validaciones estrictas de cuerpo/estados/cantidades. Sin lookups ORM o asignación de privilegios desde JSON.
- Empresa impuesta por servidor salvo POST de superadmin con empresa explícita. Company no se transfiere por actualización. Created_by e identificadores no son escribibles; creador histórico conservado ante reasignación.
- Internal_id CJ-UUID generado, QR UUID independiente, UNIQUE y reintento acotado de colisiones. Filtros autorizados por ambos identificadores y referencias.
- Categorías case-insensitive por empresa, flags frágil/perecedera coexistentes, filtros y PROTECT en borrado.
- Estados iniciales de cajas: creación REGISTERED, paso a RECEIVED/REJECTED; estados finales sin cambios efectivos/reversión ni borrado. DELETE administrativo solo REGISTERED. No se implementó Reception ni el flujo completo F6.
- Escrituras atómicas con bloqueo/relectura de actor, recurso, empresa y referencias; CHECK PostgreSQL de estados/prioridades añadido sin retirar restricciones existentes.
- Rate privado compartido 120/min por usuario, 429 y Retry-After; 500 genérico sin texto interno, SQL o credenciales. No se añadieron dependencias ni servicios.

## ARCHIVOS CREADOS O MODIFICADOS

| Archivo/grupo | Cambio |
|---|---|
| backend/apps/core/api.py | Base CRUD, serializers estrictos, permisos por acción/empresa, filtros tipados, transacciones y throttle |
| backend/apps/catalog/serializers.py y views.py | CRUD y filtros de categorías |
| backend/apps/boxes/serializers.py y views.py | CRUD, FK, lectura contextual, estados, identificadores y colisiones |
| backend/apps/catalog/models.py | Nombre recortado/no vacío |
| backend/apps/boxes/models.py | CHECK de estados/prioridades y creador histórico inmutable/válido tras reasignación |
| backend/apps/boxes/migrations/0002_box_box_status_allowed_box_box_priority_allowed.py | Nueva migración CHECK PostgreSQL |
| backend/apps/core/errors.py | Respuesta segura ante excepción DRF inesperada; log solo clase |
| backend/config/urls.py y settings/base.py | Rutas versionadas y límite privado |
| backend/tests/test_crud.py | 79 casos nuevos, parametrizados, multiempresa, concurrencia e integración HTTP |
| scripts/verificar_fase3.py | Verificación reproducible con evidencia saneada |
| scripts/verificar_fase2.py | Protección de evidencia histórica F2 contra ejecución sobre F3 |
| README y docs | Contrato, pruebas, seguridad, permisos, datos, arquitectura, plan, matriz, decisiones y diseño actualizados; este informe |
| docs/evidencias/fase3-* | Línea base F2 observada, salida de migración y verificación final |

Frontend no modificado. Se conservan fuentes y aspecto provisionales F1. No se modificó Android, .env, configuración de red/puertos o recursos cloud.

## PRUEBAS EJECUTADAS

[fase3-verificacion.json](evidencias/fase3-verificacion.json): **19 comprobaciones con código 0**, reproducibles con `python scripts/verificar_fase3.py`.

- **146 pruebas aprobadas en 14.02 s** en la ejecución final: 67 casos de regresión F2 + 79 F3.
- PostgreSQL 17.11 real y base test_ desde cero; Custom User en primera migración y ausencia de auth_user conservados.
- CRUD positivo/negativo, todos los roles, dos empresas, UUID ajeno, filtros y JSON manipulados, FK externas, cantidades/pesos/estados, unicidad y borrados.
- Datos relacionados incoherentes desde SQL externo no se sirven ni enlazan por API.
- Colisión de identificador: regeneración probada; agotamiento de tres intentos 409.
- Dos actores/conexiones sincronizados: categoría duplicada 201/409 y estados opuestos de caja 200/409.
- Rate limit real de 120 lecturas secuenciales, 429/Retry-After, usuario independiente y recuperación de ventana. No es una prueba de rendimiento/carga.
- 500 inyectado solo en tests, JSON genérico aun con DEBUG de prueba, sin ruta pública que provoque errores.
- **15 solicitudes HTTP reales** mediante servidor efímero con PostgreSQL test_: CRUD, anónimo 401, operador DELETE 403, detalle ajeno 404 y FK ajena 400. Códigos registrados en la evidencia; sin fixtures de negocio permanentes en DB principal.
- Migración aplicada conservando el volumen: [salida real](evidencias/fase3-migraciones.txt). Migrate y makemigrations sin pendientes después de aplicar.
- Ruff, ESLint y build frontend aprobados; health real directo/proxy 200, CRUD del servidor principal sin token 401.

La prueba HTTP de CRUD usa servidor de pruebas local, no infraestructura cloud ni interacción visual de un usuario. No se utilizaron SQLite, un hasher débil o controles desactivados para aprobar.

## ERRORES Y LIMITACIONES

Se corrigió un import de Decimal detectado por lint y el primer comando de migración; después se generó/aplicó correctamente y pasó la suite. Se corrigieron imports/formato y una línea larga del verificador. La validación del creador fue ajustada para conservar la trazabilidad al reasignar usuarios, con regresión positiva e inmutabilidad verificadas.

No quedan errores críticos conocidos en F3. Persisten W005/W021 de HSTS para producción, no silenciadas. El rate limiting es por proceso/no atómico entre workers; no se promete protección distribuida. La API valida y filtra las vías expuestas, pero no existen RLS/triggers cruzados que impidan todo SQL administrativo directo.

Listas iniciales sin paginación. Productos, sucursales y empresas siguen preparándose mediante el Admin restringido, sin CRUD público adicional; la interfaz F4 deberá usar referencias de configuración autorizadas. No se implementaron historial, recepción completa, cámara/QR, estadísticas, backups, TLS externo ni carga. No se contactó al VPS ni se inventó auditoría Android.

## SEGURIDAD

Permisos y pertenencia se comprueban en el servidor. Empresa/creador/identificadores protegidos, FK validadas y revalidadas bajo transacción, lecturas filtradas antes de búsqueda/detalle y errores de referencias no disponibles genéricos. Borrados coherentes con PROTECT/estado. JSON inesperado/extra rechazado; no se aceptan filtros arbitrarios.

Secretos fuera de Git, sin tokens/cookies/passwords en evidencias. PostgreSQL continúa sin puerto publicado; web/API solo en loopback, procesos web no root. El servidor HTTP efímero de test no publicó puertos al host ni dejó datos persistentes. No hay despliegue, recurso remoto o servicio de pago nuevo.

## DOCUMENTACIÓN Y DECISIÓN VISUAL

ENDPOINTS documenta rutas, cuerpos, permisos, filtros y respuestas; PRUEBAS enlaza resultados; SEGURIDAD/ROLES precisan cobertura y límites; MATRIZ refleja API completada y UI/validación final pendientes. BASE_DE_DATOS y DECISIONES registran la migración y políticas iniciales.

Para futura F4 queda registrada **A como base principal, con recursos oscuros de marca inspirados en B; sin segundo tema completo**, manteniendo accesibilidad, identidad y operación. DISENO_UI_UX y el brief para Stitch se actualizaron documentalmente. No se rediseñó ninguna pantalla ni se generaron nuevos activos de interfaz.

## CHECKLIST HUMANO

- Revisar este informe, el contrato y las reglas de estados/borrado.
- Si se desea probar manualmente datos propios, crear superadmin con prompt local, configurar empresa/productos/sucursales y usar un cliente HTTP seguro. No pegar tokens o contraseñas en el chat.
- Autorizar F4 por separado cuando corresponda. No hace falta repetir las verificaciones automatizadas ya registradas.
- Antes de F5, confirmar rúbrica/cuenta académica y autorizar expresamente cualquier recurso cloud. El entorno cloud aún no está evaluado.

SIGUIENTE FASE: F4 — frontend funcional conectado a la API y diseño A con recursos de B, únicamente cuando se autorice.

AUTORIZACIÓN: **Detenido para revisión. No iniciar F4 ni F5 automáticamente.**
