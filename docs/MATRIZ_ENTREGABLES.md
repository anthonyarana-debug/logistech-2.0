# Matriz de requisitos y evidencias

## F6, Bloque 2

| Entregable | Estado | Evidencia |
|---|---|---|
| QR/etiqueta/resolución autenticada | Implementado, SVG vectorial y decodificación independiente | test_identification.py, E2E y capturas |
| Cámara web | Implementada con soporte nativo y permiso voluntario; cámara física pendiente de comprobación humana | Denegación SIMULADA documentada, alternativa manual real |
| Recepción única/transaccional/idempotente | Implementada con PostgreSQL real | test_reception.py, hilos/concurrencia/rollback y E2E replay |
| Historia persistente | Read-only REST/ORM y triggers PostgreSQL; datos históricos previos no inventados | Tests SQL, migraciones y eventos reales |
| Contratos web/móvil | REST documentado, Android no modificado ni integrado | ENDPOINTS y ANDROID_COMPATIBILIDAD |
| Indicadores operativos | Conteos reales de recepciones/eventos por ámbito | Overview y E2E |
| Stock/movimientos/reportes | Pendientes de siguientes bloques | PLAN_FASE_6 |
| Cloud | Preparación parcial, sin provisión ni despliegue | CLOUD_FASE_6 |

Resultados finales y limitaciones: INFORME_FASE_6_BLOQUE_2.md. Matrices previas conservan su carácter histórico.

## Estado funcional F6 — bloque 1

| Entregable | Resultado local | Evidencia |
|---|---|---|
| Empresas, sucursales, productos y usuarios | REST y pantallas reales; categorías/cajas previas conservadas | operations.spec.js, test_operations.py |
| Permisos y aislamiento | Dos empresas, campos protegidos, roles, desactivación y referencias negativas | Suite PostgreSQL; ENDPOINTS.md |
| Migraciones seguras | Tres 0002 aditivas; actualización desde 0001 con datos históricos | test_f6_migrations.py |
| Paneles por rol e idioma | Recuentos reales; inglés predeterminado; responsive/axe | E2E y unitarias de catálogo |
| Integración y verificación | Resultados finales y archivos en INFORME_FASE_6.md | evidencias/fase6/ |
| QR/recepción/movimientos/stock/auditoría/Android | Diseñados como siguientes bloques, no implementados | PLAN_FASE_6.md |
| Cloud | Preparación parcial, sin despliegue | CLOUD_FASE_6.md |

Las matrices académicas y validaciones F0–F5 que siguen permanecen históricas. La autorización funcional F6 supera el alcance del 25 %, sin declarar terminados F7/F8.

Actualización FASE 5 (2026-10-27): **12 requisitos completados localmente y 1 parcial (cloud)**. Validación local aprobada, entrega global PARCIAL si se exige cloud activo; no hay despliegue externo verificado. Código/prueba/resultado/evidencia/pendiente individual en CHECKLIST_SEMANA_11.md. 156 backend + 5 JS + 9 E2E; carga API 50/100 con límites explícitos. Zoom nativo/lector/tacto físico pendientes humanos. F6–F8 no iniciadas.

Adaptación posterior: [matriz de la guía del profesor](MATRIZ_GUIA_PROFESOR.md), [informe académico](INFORME_ACADEMICO.md) y [cierre del ajuste](INFORME_ADAPTACION.md). Sin nuevas funciones F6–F8; cloud continúa parcial.

## Prioridad: entrega del 25 %

| ID | Requisito | Fase responsable | Criterio verificable / evidencia prevista | Estado real |
|---|---|---|---|---|
| 25-01 | Entorno cloud evaluable | F1/F5; despliegue separado autorizado | Configuración, guía, URL autorizada y health comprobado si lo exige la rúbrica | PARCIAL: artefacto Gunicorn/variables/guía, sin proxy/TLS/DB cloud ni URL verificados |
| 25-02 | Endpoints funcionales y documentados | F2/F3 | Método/ruta/parámetros/auth/respuestas/ejemplos en ENDPOINTS y pruebas HTTP reales | Salud/auth/CRUD categorías y cajas implementados y documentados |
| 25-03 | Registro y login separados | F2/F4 | Usuario nuevo operador sin empresa, login válido/inválido y flujo web | Formularios conectados y E2E, asignación pendiente explícita |
| 25-04 | Rate limiting | F2/F3/F5 | Límites documentados, 429 y Retry-After, recuperación de ventana; limitaciones de caché explícitas | COMPLETADO local: auth/CRUD, 429 real de refresh y ventanas probadas; LocMem no distribuido |
| 25-05 | 404, 403 y módulo en desarrollo | F4 | Navegación real y pruebas; API conserva JSON y códigos propios | Vistas en inglés tras adaptación, manejo de errores y rutas implementados; F4 E2E |
| 25-06 | 200/201/204/400/401/403/404/429/500 | F2/F3/F5 | Casos positivos/negativos y fallo inyectado solo en prueba; 204 sin cuerpo | COMPLETADO local: reejecutados F5, 405/409/503 adicionales; 500 inyectado seguro sin ruta pública |
| 25-07 | CRUD categorías y cajas | F2/F3/F4 | Crear/leer/editar/borrar con roles, FK coherentes, validaciones y pruebas cruzadas | REST y formularios reales probados; estados finales protegidos y DELETE confirmado |
| 25-08 | Variables de entorno | F1/F5 | .env.example ficticio, secretos ignorados, config por entorno y arranque comprobado | COMPLETADO local: configuración y políticas F5 probadas; secretos cloud humanos |
| 25-09 | Hash de contraseñas | F2 | Valor almacenado distinto al original y check_password correcto | PBKDF2-SHA256 y validadores probados con hashing real |
| 25-10 | Pruebas unitarias | F2/F3/F4/F5 | pytest, unitarias JS y E2E; resultados reales y pruebas trazables | COMPLETADO: 156 pytest + 5 Node + 9 E2E F5, inicial con 3 fallos por 429 conservado |
| 25-11 | PostgreSQL y migraciones | F1/F2/F3/F5 | Conexión real, base desde cero, migraciones versionadas y sin cambios pendientes | F2 y CHECK de estados/prioridades F3 aplicados; User 0001 sin auth_user; base test desde cero y sin pendientes |
| 25-12 | Diagrama ER editable | F0/F2/F5 | Fuente Mermaid contrastada con modelos/migraciones reales | COMPLETADO: columnas comparadas sin diferencias, SVG/PNG renderizados e inspeccionados |
| 25-13 | Carga inicial 50–100 usuarios | F5 | CSV e informe: usuarios alcanzados, spawn, duración, RPS, media, p95 y fallos | COMPLETADO local delimitado: 50/100 activos, 0 fallos HTTP; login fixture/CSV de cierre documentados |

## Requisitos transversales

| ID | Requisito | Fase / prueba prevista | Estado |
|---|---|---|---|
| T-01 | Backend Django/DRF, React/Vite/JS/Tailwind, PostgreSQL | F1: arranque/build e integración PostgreSQL | Base configurada y comprobada localmente |
| T-02 | JWT mantenido y compatible | F1 selección; F2 emisión/refresh/expiración/revocación según política | Auth real, rotación, blacklist, expiración, inactividad y concurrencia probadas |
| T-03 | Tres roles explícitos y mínimo privilegio | F2/F3: matriz en ROLES_PERMISOS y casos por rol | Permisos reales CRUD por rol/empresa probados; roles avanzados F6 pendientes |
| T-04 | Evitar autoasignación y aislamiento entre empresas | F2/F3: dos empresas, lista/detalle/FK, operador sin empresa, flags privilegiados | Listas/detalles/edición/FK/filtros/JSON probados con dos empresas; referencias incoherentes externas excluidas |
| T-05 | Superadmin seguro y flags coherentes | F2: createsuperuser y formularios/gestores administrativos | Gestor, forms, CHECK DB y Admin restringido probados; sin credencial automática |
| T-06 | Identificación independiente del QR | F2/F3: UNIQUE, generación automática y consulta por ambos identificadores | Generación, búsqueda autorizada por internal_id/qr_code y reintento acotado de colisiones probados |
| T-07 | Categorías frágiles y perecederas | F2/F3: flags independientes, validación y persistencia | Modelo/CRUD/flags coexistentes y filtros probados |
| T-08 | Empresas y sucursales | F2 núcleo mínimo; F6 administración completa | Modelos mínimos/Admin restringido disponibles; administración web completa F6 pendiente |
| T-09 | Interfaz inglesa por defecto y responsive | F4: escritorio/móvil, teclado y estados de error/carga | Implementada y adaptada al inglés; anchos 320/390/768/1440 y axe; zoom CSS 200%; lector/zoom nativo/táctil físico pendientes humanos |
| T-10 | HTTPS, CORS, secretos, red privada | F1 configuración; F5 preparación; despliegue/F7 verificación externa | PARCIAL: producción SSL/cookies/proxy opt-in preparados; TLS/CA/red cloud sin verificación |
| T-11 | No depender ni sobrescribir Android/VPS | F0: no hay fuentes originales; API propia planificada | Restricción respetada; compatibilidad no verificada |
| T-12 | Git y commits por fase, sin secretos | F1 en adelante: diff e historial local; nunca push implícito | F0–F5 publicados en GitHub, ahora público; adaptación solo local hasta revisión; secretos y artefactos ignorados |
| T-13 | Salud de servicio | F1: respuesta y conectividad DB; 503 si dependencia falla | Comprobado: 200 con DB, 503 al detenerla y recuperación posterior |
| T-14 | Datos demo identificados y controlados | F4: comando explícito con namespace, archivo privado y pruebas | create_demo, dos empresas DEMO y cuatro roles, claves aleatorias, sin sobrescritura |
| T-15 | Documentación completa en español | F0–F5 ampliación según PLAN | F3 incluye contrato CRUD, pruebas, seguridad, roles, decisiones y cierre; revisión final F5 pendiente |
| T-16 | Auditoría, backup y observabilidad | F6/F7: eventos sin secretos, restore y recuperación comprobados | Solo planificado |
| T-17 | Escaneo QR en navegador móvil | F6: HTTPS, cámara y alternativa manual reales | Diferido, no implementado |

## Entregas futuras sin autorización de implementación

| Entrega | Alcance | Evidencia requerida posteriormente | Estado |
|---|---|---|---|
| 80 % / F6 | CRUD ampliado, paginación, permisos completos, inventario/recepciones, reportes, tokens, backups y cloud | Integración por rol/empresa, restauración y métricas 1000–5000 usuarios autorizados | No autorizada |
| Operación / F7 | HTTPS, redes, secretos, monitoreo, logs, fallos y recuperación | Comprobaciones externas y simulación autorizada | No autorizada |
| 100 % / F8 | Sistema integral, observabilidad y optimización | Evidencias de carga 10000–50000 solo con capacidad/permiso y recuperación medida | No autorizada |
| Opcionales | Google OAuth, OCR, VPC, CI/CD, balanceo | Justificación y aceptación específica según necesidad | No comprometidos para el 25 % |

## CHECKLIST HUMANO

- Confirmar con el profesor si el 25 % exige despliegue cloud activo o admite configuración preparada; hasta entonces no darlo por cumplido.
- Confirmar objetivos de rendimiento y plazo académico antes de evaluar resultados.
- Revisar F3 y decidir si se autoriza F4; no se avanzará automáticamente.
