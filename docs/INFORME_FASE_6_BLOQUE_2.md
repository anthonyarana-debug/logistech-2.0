# Informe Fase 6, Bloque 2 — identificación QR, recepción y trazabilidad

Fecha: 28 de octubre de 2026. Rama local: `codex/fase-6-administracion`.
Código principal: `ff58947`. Ajustes de accesibilidad/verificación: `3ad72cf`.
Estado: bloque implementado y comprobado localmente. F7 solo preparación documental;
sin despliegue cloud, contratación de recursos AWS, modificación de main ni Android.

## Recuperación y conservación

Se revisaron Git, ramas, commits, PLAN_FASE_6, INFORME_FASE_6, CLOUD_FASE_6,
ARQUITECTURA, BASE_DE_DATOS, ENDPOINTS y roles. La rama partió limpia en ca58c16.
Se reejecutaron las 216 pruebas anteriores con PostgreSQL: 216 passed in21.16s.
No se descartó trabajo, no hubo reset/clean, borrado de ramas ni volúmenes.
F0–F5, informes históricos, documento académico y Bloque1 permanecen conservados.
Internacionalización y diseño Industrial Precision continúan como base.

Docker Desktop Linux29.5.3 operativo. Se empezó en logistech-f6 aislado y se creó
logistech-f6-b2 con PostgreSQL17.11 y volumen propio para el cierre. Ambos entornos
se conservan; no se tocó la base de trabajo. El último publica solo loopback8002/5175;
PostgreSQL no publica puerto de host. Las credenciales aleatorias se guardan fuera de
Git en .env.f6-b2-final-demo.json, con ACL privada; no se reproducen aquí.

Tras auditoría inicial sin hallazgos, Git publicó el respaldo del Bloque1 en
codex/respaldo-f6-bloque-1, SHA ca58c1689427b8fa63db54faa2bbbbbd0fa10f58,
verificado con ls-remote. GitHub CLI no estaba en PATH; la autenticación Git disponible
permitió el push sin pedir ni exponer tokens. El respaldo final del Bloque2 se verifica
al cerrar, después de auditoría del índice completo. Main permanece e7e437c.

## Reglas de negocio y compatibilidad

[REGLAS_RECEPCION](REGLAS_RECEPCION.md) fija el contrato definido antes de integrar:
REGISTERED se resuelve una sola vez como RECEIVED o REJECTED, en su sucursal actual.
Rechazo requiere DAMAGED/INCORRECT_ITEM/OTHER; aceptación no admite motivo.
No hay traslado, recepción parcial, movimiento ni incremento de saldo implícitos.

POST /receipts/ exige Idempotency-Key UUID, limitado por actor/empresa. Nueva
recepción201, repetición exacta200 y recurso/clave incompatible409. Actor, empresa,
fecha y origen son del servidor; se bloquean filas y se escriben Receipt, estado y
BoxEvent en una transacción. Unicidad PostgreSQL refuerza la idempotencia y una
recepción por caja. Conflictos PostgreSQL40P01/40001 se revierten y devuelven409
seguro para reintentar la misma operación; errores desconocidos500 genéricos.

PATCH/PUT anterior mantiene enums/contrato y deriva transiciones finales al mismo
servicio, con origen BOX_STATUS_UPDATE; rechazo antiguo sin motivo queda OTHER,
sin inventar causa concreta. No-op terminal no crea otra recepción. Cajas terminales
anteriores conservan estado e identificadores sin backfill ficticio de fecha/actor.
Se comprobó migración de los tres estados anteriores con cero historia inventada.

## Funcionalidades realmente disponibles

- QR SVG determinista a partir de logistech:box:<qr_code>, visible en detalle de caja.
  UUID del modelo, qr_code e internal_id siguen independientes. No contiene secretos.
- Etiqueta SVG vectorial descargada con autenticación, 100×80mm, QR y referencia
  legible. Generación local en memoria con qrcode8.2; sin servicio externo ni bucket.
- Identificación exacta por payload QR, UUID QR o CJ-internal_id; cuerpo de caja
  autorizado y mismo404 para códigos ajenos/inexistentes. UUID de modelo no resuelve
  como qr_code. No se abren enlaces arbitrarios escaneados.
- Cámara web con activación explícita, BarcodeDetector/contexto seguro y permiso;
  detención/liberación del stream y entrada manual alternativa. No se suben imágenes.
- Recepciones reales por los tres roles autorizados en su empresa, formulario de
  aceptación/rechazo, validaciones, lista y errores claros. User.branch continúa
  organizativa; no se inventa una ACL por sucursal.
- Reintento web mantiene clave/cuerpo mientras vive el formulario, incluso si el
  servidor confirmó pero el navegador perdió respuesta. Tras recarga/navegación no
  promete conservar esa clave: Android deberá persistir su cola privada de comandos.
- Historial persistente de creación/edición/borrado de caja y recepción; lectura
  por empresa/caja, actor, fecha, resultado y detalles legibles desplegables.
  Eventos conservan snapshot UUID de cajas borradas conforme al CRUD REGISTERED.
- Indicadores reales counts.receipts/events, navegación Identify/Receptions/History,
  enlaces desde caja y paneles previos conservados. No se simulan estadísticas de stock.
- Interfaz inglesa, claves locales y datos de negocio sin traducir. Se corrigieron
  textos obsoletos de landing/estado inicial sin renombrar claves ni contratos.

## Seguridad e inmutabilidad

SUPERADMIN válido opera globalmente; COMPANY_ADMIN/OPERATOR asignados solo en empresa
activa. Pendientes y cuentas desactivadas no acceden. Se conservan protección root,
campos protegidos, CSRF/JWT, rotación, errores seguros y cuotas originales.

Receipt y BoxEvent no admiten UPDATE/DELETE desde REST ni ORM; triggers PostgreSQL
rechazan esas operaciones incluso mediante SQL ordinario. Event data está acotado y
permitido: UUID de producto/sucursal/recibo, cantidad, peso, prioridad, estado y origen/
resultado/motivo. No incluye passwords, JWT, clave de idempotencia ni notas libres.
Empresa/actor/sucursal históricos PROTECT; caja de evento es UUID snapshot sin FK
para conservar borrados permitidos, mientras Receipt sí protege su caja.

No es un registro criptográficamente inviolable frente al propietario de DB o
TRUNCATE/alteración de esquema. FKs simples no garantizan por sí solas igualdad de
empresa entre tablas; servicio/modelos mantienen esa validación. Actores pueden ser
reasignados sin reescribir su historia. Catálogos se identifican por UUID, sin afirmar
que todos sus nombres históricos se hayan versionado.

## Migraciones y archivos

Dos migraciones nuevas, aditivas, sin modificar las anteriores:

1. boxes/0003_boxevent_receipt.py: tablas Receipt/BoxEvent, FK, UNIQUE, CHECK e índices.
2. boxes/0004_immutable_reception_history.py: triggers de inmutabilidad PostgreSQL.

Aplicadas solo a bases de validación. La base de trabajo requiere backup/restauración
y ventana de migración aprobada antes de adoptar el esquema; no se migró aquí.

Archivos de código, pruebas y ejecución modificados respecto al Bloque1:

- `backend/apps/accounts/operations.py`
- `backend/apps/accounts/password_errors.py`
- `backend/apps/accounts/serializers.py`
- `backend/apps/boxes/identification.py`
- `backend/apps/boxes/migrations/0003_boxevent_receipt.py`
- `backend/apps/boxes/migrations/0004_immutable_reception_history.py`
- `backend/apps/boxes/models.py`
- `backend/apps/boxes/reception.py`
- `backend/apps/boxes/serializers.py`
- `backend/apps/boxes/views.py`
- `backend/apps/core/overview.py`
- `backend/config/urls.py`
- `backend/requirements-dev.txt`
- `backend/requirements.txt`
- `backend/tests/test_identification.py`
- `backend/tests/test_password_labels.py`
- `backend/tests/test_reception.py`
- `backend/tests/test_traceability_migrations.py`
- `compose.traceability-validation.yml`
- `frontend/e2e/flows.spec.js`
- `frontend/e2e/operations.spec.js`
- `frontend/e2e/traceability.spec.js`
- `frontend/src/components/AppShell.jsx`
- `frontend/src/i18n/en.js`
- `frontend/src/main.jsx`
- `frontend/src/pages/BoxDetail.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/pages/History.jsx`
- `frontend/src/pages/Identification.jsx`
- `frontend/src/pages/Receptions.jsx`
- `frontend/src/services/api.js`
- `frontend/src/services/traceability.js`
- `frontend/src/styles/index.css`
- `frontend/unit/traceability.test.js`
- `scripts/check_traceability_integrity.py`
- `scripts/verify_f6_block2.py`

Documentos vigentes actualizados: README, ARQUITECTURA, BASE_DE_DATOS, MODELO_DATOS.mmd,
ENDPOINTS, API_INTERNA, ROLES_PERMISOS, SEGURIDAD, DECISIONES_TECNICAS,
MATRIZ_ENTREGABLES, PRUEBAS, PLAN_FASE_6 y CLOUD_FASE_6. Nuevos REGLAS_RECEPCION,
ANDROID_COMPATIBILIDAD, este informe y evidencias/fase6-bloque2. Informes históricos
F0–F5, INFORME_FASE_6 e informe/documentos académicos no se modificaron.

## Resultados reales

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Baseline Bloque1 PostgreSQL | 216 passed in21.16s | baseline.json |
| Backend final PostgreSQL | 273 passed in23.49s, 57 nuevas respecto a216 | checks.json |
| Unitarias frontend | 15 pass, 0 fail, descubrimiento real | checks.json |
| Playwright completo | 16 pasaron, 0 fallos/omitidas/flaky, 384.07s, 1 worker, 0 retries | e2e-verified.json |
| Validación tras último ajuste visual | 3 pasaron (landing, idioma y QR/recepción/historia ampliados), 6.59s | e2e-accessibility-final.json |
| QR/etiqueta | SVG real rasterizado por sus módulos y leído por ZXing-C++3.1.1 independiente | test_identification.py |
| Concurrencia | Hilos PostgreSQL: misma caja/diferentes actores y misma clave/actor/cajas; una resolución | test_reception.py |
| Atomicidad/errores | Fallo de evento y conflictos SQL inyectados: rollback,409/500 seguros | test_reception.py |
| Inmutabilidad | Mutaciones ORM y UPDATE/DELETE SQL reales rechazados | test_reception.py |
| Migraciones | check/migrate --check/makemigrations --check pasan; actualización conserva datos/estados | checks.json y tests de migración |
| Integridad real de base de demo | Discrepancias 0; dos triggers presentes; constraints inspeccionadas | integrity.json |
| Ruff/pip check/ESLint/Vite | Todos pasan; lint local también incluye E2E | checks.json y ejecución de cierre |
| Accesibilidad/responsive | Axe A/AA/2.1 AA en escenarios comprobados;320/390/768/1440, incluida identificación resuelta, recepción e historia | E2E y PNG |
| Secretos | Ver auditoría final de índice/historial y valores privados conocidos | secret-audit-final.json |

La regresión completa incluye auth/CSRF/refresh/caducidad real de cinco minutos,
registro, roles/administración Bloque1, categorías/cajas, permisos cruzados, errores,
campos protegidos y default inglés. No se acortó TTL ni se relajaron restricciones.

La última auditoría SQL es de solo lectura en datos aislados; cuenta 9
recepciones y 26 eventos en el instante registrado. No son datos
productivos ni métricas de rendimiento, y pueden aumentar al repetir E2E.
No se ejecutó carga Locust/k6 nueva ni pruebas Android/cloud.

## Incidencias y correcciones conservadas

- Primera integración: cinco fallos (validación no-objeto/extra que devolvía500,
  aserción UUID pre-render, expectativa de excepción en lugar de error500 seguro y
  método de identificación). Se corrigieron sin suprimir negativos ni rollback.
- E2E inicial1/3 por selectores ambiguos y puntuación; corregidos y3/3 después.
- Primera corrida completa11/16: contraseña sintética UUID coincidió con similitud
  legítima, y varias ejecuciones agotaron refresh30/hora. Se corrigió la generación
  independiente de contraseñas; se mantuvo el validador. Un label español del modelo
  apareció en su error: renderer compartido conserva plantilla/código/parámetros y
  traduce solo metadatos de campo, nunca datos del usuario.
- Corrida posterior15/16: Playwright falló al capturar raíz SVG standalone. Se
  corrigió el capturador para mostrar exactamente el SVG descargado dentro de IMG;
  no se redibujó la evidencia. Reintento posterior encontró refresh agotado: se
  conserva como fallido, no se cuenta como aprobación.
- Ejecución verificada completa16/16 con namespace independiente y proceso actualizado
  entre corridas, sin reinicios/limpieza de caché durante ninguna corrida ni cambios
  de cuotas/IP/TTL. Navegaciones SPA sustituyen recargas que no probaban restauración.
- Revisión visual: botón sobre panel oscuro tenía contraste1.36:1. Prueba axe roja lo
  detectó; se usa variante lime existente y prueba verde. Títulos largos permiten
  envolver IDs; se añadieron verificaciones móviles con resultados visibles.
- Búsqueda fallida antes conservaba selección anterior: se limpia al editar/iniciar
  consulta y no se permite recibir una caja obsoleta por fallback de formulario.
- Historia dejó de presentar JSON técnico crudo: detalles de negocio desplegables,
  estados legibles e IDs envueltos, respetando Industrial Precision.

Reportes saneados incluyen ejecuciones fallidas/intermedias, sin adjuntos privados ni
cuerpos/credenciales. Datos brutos permanecen ignorados en output/qa/f6-b2. Manifiesto
SHA-256 permite comprobar archivos; auditoría de patrones no es certificación absoluta.

## Evidencias visuales reales y límites

Se inspeccionaron QR de caja, etiqueta SVG descargada y su PNG, identificación manual,
recepción aceptada/replay/rechazada, historia compacta, identificación e historia390px.
Tablas anchas mantienen scroll horizontal interno; no se afirma que todas sus columnas
sean simultáneamente visibles en móvil. Captura camera-denial-SIMULATED está rotulada:
no se validó cámara física, iluminación, óptica ni impresión en papel. ZXing sí verificó
el contenido de los SVG emitidos, sin sustituir esa revisión de hardware.

## Android, cloud y siguientes bloques

ANDROID_COMPATIBILIDAD documenta DTO, QR, auth/cookies/CSRF/TLS, almacenamiento seguro,
rotación, estados, cola de idempotencia y errores. No se inspeccionó ni modificó el
repositorio móvil separado y no se declara integración completada.

CLOUD_FASE_6 identifica almacenamiento QR en memoria sin S3 requerido, backups de
registros/triggers/idempotencia, permisos DB, migración única y HTTPS/cámara. Cloud
continúa parcial: sin recursos pagados ni servicios externos desplegados.

Pendientes: movimientos/transferencias, unidades y recepciones parciales, saldos y
conciliación, correcciones compensatorias, reportes paginados/exportación, cuotas
compartidas y pruebas del entorno cloud. Extender eventos/CHECK mediante migraciones
antes de añadir tipos; no reescribir historia ni usar Box.quantity como saldo.

## Checklist humano

- [x] Código y dos migraciones implementados; pruebas PostgreSQL y web comprobadas.
- [x] Rama, avances anteriores, documentos históricos y base de trabajo conservados.
- [x] Capturas reales y resultados fallidos/finales preservados sin secretos.
- [ ] Probar cámara física con permiso, denegación y parada en navegadores objetivo.
- [ ] Imprimir etiqueta al100% y comprobarla con lector físico y QR deteriorado.
- [ ] Revisar aceptación/rechazo, alcance empresarial y registro histórico con usuarios.
- [ ] Backup/restauración verificados y migración planificada antes de otra base.
- [ ] Auditar Android antes de integrarlo; acordar movimiento/stock/compensación.

El commit documental final y el SHA de la rama de respaldo se informan al cierre,
evitando referencia circular al commit que contiene este informe. No hubo push a main.
