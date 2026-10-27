# Informe de cierre — Fase 2

Fecha: 27 de octubre de 2026 (America/Lima).

FASE COMPLETADA: Modelos y autenticación, con preparación documental de diseño Industrial Precision.

ESTADO: **Completa en el alcance autorizado de F2.** El entregable del 25 % aún requiere CRUD REST (F3), frontend funcional (F4) y validación final (F5). No se inició F3 ni se rediseñó la interfaz.

## FUNCIONALIDADES

- Custom User por email y UUID en **accounts/0001_initial**, con rol y empresa nullable; configuración activa antes de migrar auth/Admin. PostgreSQL contiene accounts_user y no auth_user.
- Company, Branch, Category, Product y Box mínimos, migraciones versionadas, validación de pertenencia, referencias PROTECT, constraints e identificadores de caja independientes del QR. Sin endpoints CRUD aún.
- Registro público exclusivamente OPERATOR sin empresa, con validación/hash real y rechazo de campos privilegiados.
- Login separado, JWT access de 5 min, refresh HttpOnly de 1 día con rotación/blacklist, protección CSRF, identidad vigente y logout idempotente.
- Consumo único de refresh con bloqueo transaccional PostgreSQL; cuenta desactivada rechaza access y refresh.
- Rate limiting local para login IP/email, registro, refresh, logout, CSRF y login Admin; 429/Retry-After verificados.
- Admin restringido a superadmin activo, creación mediante procedimiento seguro y asignación administrativa de empresa/rol. is_staff aislado no concede alcance global.
- Documento de diseño con referencias realmente inspeccionadas, paleta contrastada, componentes, responsive, accesibilidad, rendimiento, brief para Stitch y alternativas A/B originales. La web de estado conserva su código de F1.

## ARCHIVOS

| Creaciones / modificaciones | Contenido |
|---|---|
| backend/apps/accounts | Modelo/gestor User, serializers estrictos, permisos base, throttles, vistas/rutas auth, paquete y 0001_initial |
| backend/apps/organizations | Company/Branch, bases de validación y pertenencia, 0001_initial |
| backend/apps/catalog | Category/Product mínimos, 0001_initial |
| backend/apps/boxes | Box mínimo e identificadores independientes, 0001_initial |
| backend/config | Admin restringido, auth/apps/settings/validadores/plantillas y rutas; cookie Secure en production |
| backend/apps/core/errors.py | Errores auth/CSRF JSON genéricos |
| backend/tests | conftest, test_auth, test_models_permissions, test_throttling, paquete y adaptación de infraestructura a Custom User |
| backend/tools | Verificación estructural actualizada y smoke HTTP real sin salida de secretos |
| scripts | verificar_fase2.py; verificador F1 protegido para no sobrescribir evidencia histórica |
| docs | BASE_DE_DATOS, ENDPOINTS, SEGURIDAD, ROLES_PERMISOS, DISENO_UI_UX, este informe; actualización de PRUEBAS, PLAN, ARQUITECTURA, DECISIONES_TECNICAS, DESPLIEGUE y MATRIZ_ENTREGABLES |
| docs/diagramas y diseño | MODELO_DATOS.mmd actual, MODELO_FUTURO.mmd separado; diseno/alternativa-a.svg y alternativa-b.svg originales |
| docs/evidencias | fase2-verificacion.json y fase2-contraste.json |
| README | Inicio con migraciones explícitas, contrato, pruebas actuales, Admin y límites |

No se añadieron dependencias, no se modificaron frontend/src ni recursos originales Android y no se crearon usuarios administrativos con contraseña fija.

## PRUEBAS EJECUTADAS

Evidencia: [fase2-verificacion.json](evidencias/fase2-verificacion.json), reproducible con `python scripts/verificar_fase2.py`.

- **67 pruebas aprobadas** usando PostgreSQL real y hashing PBKDF2 sin debilitar controles; duración exacta en evidencia.
- **14 comandos finales con código 0**: configuración/estado Compose, pip check, Django check, migraciones sin pendientes, introspección, suite, Ruff, frontend lint/build, check de producción y smoke HTTP.
- Migraciones generadas, plan revisado y aplicado en volumen local conservado. La suite aplica el grafo en base test_ desde cero y verifica User en la primera migración; no SQLite.
- Registro 201; login 200; identidad 401/200; CSRF 403; validación 400; límites 429; logout 204; rotación/replay e inactividad verificados.
- Dos solicitudes de renovación sincronizadas en hilos/conexiones separados: un éxito y un rechazo, sin doble consumo.
- HTTP real del servidor: me 401 → csrf 200 → register 201 → login 200 → me 200 → refresh 200 → logout 204 → refresh 401.
- Cuenta técnica del smoke desactivada al terminar, contraseña inutilizable y sin empresa/datos de inventario. Cada ejecución deja una cuenta técnica inactiva identificable.
- Pares de color calculados en sRGB; gris/lima sobre marfil descartados para texto normal. Bocetos SVG documentales, sin operaciones simuladas.

Comandos y casos trazables en [PRUEBAS.md](PRUEBAS.md). No se ejecutaron carga, cloud, Android, cámara/móvil real, TLS, backup/restauración o evaluación completa de accesibilidad. Los diagramas Mermaid están contrastados con fuentes/migraciones; su renderizado no se verificó.

## ERRORES

Corregidos: JSON de tipo incorrecto causaba errores en serializer/throttle; el test Admin sin CSRF no alcanzaba el throttle; un smoke auxiliar usaba loopback del contenedor equivocado; FK inexistente podía escapar como DoesNotExist; ajustes de imports/formato. Las comprobaciones afectadas se repitieron.

No quedan errores críticos conocidos en F2. check --deploy conserva advertencias W005/W021 de HSTS. El uso compartido de IP, los contadores por proceso, el rol PostgreSQL administrador local y los estáticos/servidor de producción deben resolverse en el despliegue autorizado correspondiente. La ausencia de código Android sigue registrada, sin auditoría inventada.

Los SVG conceptuales pasaron validación XML; su renderizado local no pudo comprobarse: el navegador bloqueó file:// y el visor no admite SVG. Esta limitación queda registrada, sin eludir el bloqueo ni afectar la verificación técnica del backend.

## SEGURIDAD

Registro sin autoasignación; CHECK DB de flags/rol, UNIQUE email case-insensitive, hash seguro, cookies protegidas y CSRF, validación de usuario activo, errores genéricos, no-store y rate limiting probado localmente. Sin secretos en el repositorio ni salida de pruebas. Red/puertos de F1 conservados y sin servicios públicos nuevos.

Límites importantes: logout revoca el refresh presentado, pero access previo puede durar hasta 5 minutos; no se promete logout de todos los dispositivos. Rate limiting no es distribuido ni DDoS. Política de empresa y modelos no sustituyen autorización/querysets CRUD de F3. No se desplegó producción ni se solicitó/contrató infraestructura externa.

## DOCUMENTACIÓN Y DISEÑO

[DISENO_UI_UX.md](DISENO_UI_UX.md) contiene investigación de los cinco sitios y limitaciones de acceso, sistema propuesto y brief reutilizable en Google Stitch. No se usó una sesión o servicio de Stitch ni se le enviaron datos.

Alternativas: **A / Hoja de control** (marfil, navegación petróleo y enfoque editorial/operacional, recomendada) y **B / Terminal de trazabilidad** (oscura, registro técnico y detalle contextual). [Boceto A](diseno/alternativa-a.svg) y [boceto B](diseno/alternativa-b.svg). Son composiciones conceptuales originales. La elección queda abierta antes del rediseño de F4.

Diagrama actual y futuro separados; contrato auth, base de datos, seguridad y matriz de roles actualizados. Evidencia F1 preservada como histórica.

## CHECKLIST HUMANO

- Revisar este informe y autorizar F3 por separado cuando corresponda.
- Si se desea revisar el Admin, crear superadministrador con `docker compose exec backend python manage.py createsuperuser` y usar el prompt local; no enviar la contraseña al chat.
- Elegir A/B antes de autorizar el rediseño de F4. Stitch es opcional y no bloquea el backend.
- Facilitar el Android original si está disponible; antes de F5 confirmar rúbrica/cuenta académica y autorizar cualquier recurso cloud por separado.

SIGUIENTE FASE: F3 — API/CRUD inicial de categorías y cajas con filtros, permisos por acción/empresa, validaciones y pruebas de endpoints reales.

AUTORIZACIÓN: **Esperando confirmación del usuario. No avanzar automáticamente a F3.**
