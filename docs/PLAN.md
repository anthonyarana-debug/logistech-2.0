# Plan de desarrollo y validación

Plan original: 2026-10-26. Actualización: 2026-10-27. FASE 4 autorizada e implementada localmente: frontend A con recursos oscuros de B, sesión y CRUD reales. Ver INFORME_FASE_4.md y PRUEBAS.md para evidencias y límites de validación. **F5–F8 no iniciadas; se espera revisión y nueva autorización. El 25 % no se declara completo.**

## Reglas de avance

Detenerse al finalizar cada fase y presentar informe con estado, archivos, comandos/resultados, errores, seguridad, documentación, checklist humano y siguiente fase. F6, F7 y F8 requieren autorización expresa adicional. No crear recursos cloud, publicar ni contratar servicios sin autorización. Los commits futuros serán locales, revisando antes el diff y ausencia de secretos; no se creó commit en F0.

## F0 — Auditoría y planificación

Entregados AUDITORIA.md, ARQUITECTURA.md, PLAN.md, MATRIZ_ENTREGABLES.md, diagrama conceptual editable e informe. Validación: inspección local y comprobación de archivos/enlaces. Ausencias del original y cloud documentadas, sin bloquear la planificación.

CHECKLIST HUMANO: revisar y autorizar F1; iniciar Docker Desktop; facilitar el original cuando esté disponible.

## F1 — Configuración inicial

1. Resolver acceso al motor Docker. Elegir versiones mantenidas y compatibles mediante metadatos oficiales e instalación aislada; no modificar Python global. Congelar dependencias reproducibles.
2. Crear configuración Django/DRF y health; React/Vite/JavaScript/Tailwind/Router; Fetch como cliente. Incluir Python/Node y PostgreSQL en Compose con healthchecks, red privada y volumen local.
3. Separar ajustes development/production, preparar .env.example ficticio, .gitignore, README y Dockerfiles. No publicar recursos remotos.
4. Mantener auth/admin sin activar hasta crear User en F2; ejecutar el mecanismo de migraciones de la base inicial sin generar tablas auth con User estándar. Documentar exactamente qué migraciones se aplicaron, incluso si aún no hay migraciones de negocio.
5. Verificar `docker compose config --quiet`, construcción, servicios saludables, conexión PostgreSQL y consulta real, `manage.py check`, `manage.py migrate`/`showmigrations` de apps habilitadas, health 200/503 y frontend iniciado/compilable. Guardar comandos y salidas saneadas en docs/PRUEBAS.md.

Salida: base ejecutable localmente sin CRUD ni login, evidencias reales. Si Docker sigue inaccesible, informar F1 parcial; no sustituir PostgreSQL por SQLite para declarar éxito.

CHECKLIST HUMANO: acceso a Docker Desktop si requiere interacción; revisar evidencia y autorizar F2.

## F2 — Modelos y autenticación

1. Crear User propio antes de migrar auth/admin; email, roles, flags y empresa. Implementar Company/Branch/Category/Product/Box mínimos según arquitectura; fixtures o comando demo claramente identificados, sin credenciales incorporadas al repositorio.
2. Migraciones versionadas, restricciones e identificadores. `createsuperuser` coherente y asignación administrativa restringida. Diagrama actualizado al esquema real.
3. Registro, login, refresh, identidad y cierre de sesión; JWT compatible con decisión de almacenamiento segura. Iniciar rate limiting de autenticación en esta fase, completar scopes en F3.
4. pytest/pytest-django sobre PostgreSQL: registro 201, hash y check_password, duplicados de email, credenciales inválidas, inactividad, tokens expirados, campos privilegiados rechazados, operador sin empresa, permisos de procedimientos administrativos. Verificar migración desde base vacía y ausencia de migraciones pendientes.

Salida: autenticación verificable, esquema real y docs/BASE_DE_DATOS.md, SEGURIDAD.md, ROLES_PERMISOS.md, ENDPOINTS.md y PRUEBAS.md con estado real.

CHECKLIST HUMANO: crear credencial administrativa local mediante prompt seguro de createsuperuser cuando sea necesario; revisar y autorizar F3. Nunca enviar credenciales al chat.

## F3 — API y CRUD

1. CRUD categorías/cajas con permisos por rol, filtros por empresa, pertenencia de FK, creador y empresa impuestos por servidor; transacciones y validaciones.
2. Consulta por internal_id o QR restringida; unicidad en DB y tratamiento de colisiones. DELETE con PROTECT y conflictos documentados.
3. Respuestas JSON consistentes y rate limiting de API. ENDPOINTS.md incluirá método, ruta, parámetros, cuerpo, autenticación, respuestas y ejemplos ejecutables sin secretos.
4. Pruebas CRUD reales y negativas con dos empresas, listas/detalles/referencias cruzadas, operador sin empresa, intentos de cambiar creador/empresa, 204 sin cuerpo, 400/401/403/404/409/429 y 500 controlado mediante inyección de fallo en pruebas. No exponer un endpoint público que provoque errores artificiales.

Salida: operaciones reales verificadas con PostgreSQL, matriz de permisos enlazada a pruebas por nombre.

CHECKLIST HUMANO: revisar y autorizar F4.

## F4 — Frontend funcional

1. Landing, registro, login, dashboard, categorías y cajas con API real; formularios accesibles, cargas, estados vacíos, mensajes en español y navegación responsive.
2. Guardas de interfaz complementan permisos backend. Mostrar cuenta sin asignación sin revelar datos privados. Al expirar access, renovar una vez; si falla, terminar sesión sin bucle.
3. Páginas 403/404, módulo en desarrollo y error de servicio. No incluir cifras de negocio ficticias.
4. Ejecutar build y lint; probar flujos completos en escritorio y móvil, teclado, mensajes de validación, sesión expirada y API desconectada. Registrar resultados manuales; automatización de navegador solo si aporta cobertura, sin Vitest. No presentar prueba manual como suite automatizada.

Salida: demostración web funcional de los casos aprobados, evidencia real y documentación actualizada.

CHECKLIST HUMANO: revisar experiencia y autorizar F5.

## F5 — Validación del 25 %

1. Ejecutar suite, integración PostgreSQL, permisos y limitación; revisar errores, migraciones, dependencias, configuración y diagrama.
2. Locust local: smoke inicial; después 50 usuarios a 5 usuarios/s y 100 a 10 usuarios/s, 3 minutos por escenario, con calentamiento separado de 30 s. Datos y cuentas de prueba por empresa preparados previamente; sin crear datos ilimitados ni probar servicios ajenos.
3. Mezcla propuesta: cada usuario inicia sesión una vez; consultas de cajas/categorías y detalles predominantes; creación autorizada limitada y limpieza restringida a dataset de prueba. Separar escenario de rechazo por throttling del de capacidad normal. Mantener políticas normales activas y registrar cuándo 429 afecta los resultados; no desactivar seguridad para obtener métricas mejores.
4. Exportar CSV de Locust e informe con entorno, recursos, usuarios configurados y realmente alcanzados, spawn rate, duración, RPS, media, p95, errores por tipo y porcentaje fallido. Documentar diferencia entre usuarios simultáneos y RPS. No extrapolar a cloud ni afirmar 100 usuarios sin evidencia.
5. Preparar docs/DESPLIEGUE.md con alternativa académica a confirmar: frontend estático, proceso Django de producción y PostgreSQL privado. Instrucciones de secretos fuera de Git, HTTPS, restricciones de red, migración, health y rollback. Ningún proveedor ni recurso queda contratado por esta planificación.
6. Si la rúbrica exige cloud activo, marcar ese requisito pendiente hasta despliegue autorizado y comprobado; la preparación local/documental no lo cumple por sí sola. Crear guion de demo, checklist 25 %, reporte y pendientes humanos.

Criterio: no ocultar fallos ni inventar umbrales académicos. Latencia y tasa de fallos se reportarán con datos; objetivos de aceptación del profesor quedan por confirmar. Si hay fallos sin resolver o cloud obligatorio sin validar, estado parcial.

CHECKLIST HUMANO: confirmar cuenta académica, cuotas/costos, rúbrica cloud y autorizar por separado cualquier despliegue; configurar secretos mediante herramientas locales o gestor cloud, nunca por chat. Revisar cierre y decidir si autoriza F6.

## F6–F8 — Solo planificación, no autorizadas

| Fase | Trabajo futuro | Dependencias | Evidencia futura |
|---|---|---|---|
| F6 / 80 % | Inventario, recepción, movimientos, pedidos, QR móvil, trazabilidad, sucursales asignadas, roles completos, paginación, dashboards, backups; OAuth opcional | F5 aprobada, reglas de negocio y autorización nueva | Flujos integrales, restore, roles y carga 1000–5000 solo con recursos autorizados |
| F7 / operación cloud | HTTPS, red, secretos, limitación compartida, logs estructurados, monitoreo, recuperación y despliegue | Infraestructura autorizada, presupuesto y políticas | Verificación externa, seguridad y restauración real |
| F8 / 100 % | Validación integral, optimización, fallos/recuperación y documentación final | F6/F7 verificadas, capacidad y autorización de carga | Métricas y tiempos observados; 10000–50000 usuarios solo si recursos lo permiten |

CI/CD, balanceo y escalado se decidirán por necesidad medida. El escaneo móvil requiere evaluar HTTPS y permisos de cámara. No prometer esos volúmenes por el solo diseño.

## Documentación por mantener

Los cuatro documentos de F0 se actualizan al cambiar decisiones. F1 inicia README, PRUEBAS y DESPLIEGUE; F2 inicia BASE_DE_DATOS, SEGURIDAD, ROLES_PERMISOS, ENDPOINTS y DECISIONES_TECNICAS (trasladar ADR propuestos); F3 completa contratos; F4 registra UX; F5 consolida evidencias, checklist y limitaciones. No crear carpetas vacías ni marcar documentos futuros como entregados.
