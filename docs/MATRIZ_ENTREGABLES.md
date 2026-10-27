# Matriz de requisitos y evidencias

Actualización al cierre de FASE 3 (2026-10-27): autenticación y CRUD REST iniciales verificados con PostgreSQL real. «Pendiente» conserva el alcance que falta; el 25 % sigue incompleto hasta F4/F5 autorizadas. Evidencias en PRUEBAS.md e INFORME_FASE_3.md. Dirección visual futura registrada: A con recursos oscuros de B, sin segundo tema; frontend intacto.

## Prioridad: entrega del 25 %

| ID | Requisito | Fase responsable | Criterio verificable / evidencia prevista | Estado real |
|---|---|---|---|---|
| 25-01 | Entorno cloud evaluable | F1/F5; despliegue separado autorizado | Configuración, guía, URL autorizada y health comprobado si lo exige la rúbrica | Pendiente; sin cuenta ni recursos verificados |
| 25-02 | Endpoints funcionales y documentados | F2/F3 | Método/ruta/parámetros/auth/respuestas/ejemplos en ENDPOINTS y pruebas HTTP reales | Salud/auth/CRUD categorías y cajas implementados y documentados |
| 25-03 | Registro y login separados | F2/F4 | Usuario nuevo operador sin empresa, login válido/inválido y flujo web | REST verificado F2; formularios web F4 pendientes |
| 25-04 | Rate limiting | F2/F3/F5 | Límites documentados, 429 y Retry-After, recuperación de ventana; limitaciones de caché explícitas | Auth + CRUD 120/min/usuario probados localmente; revisión F5 pendiente; no distribuido |
| 25-05 | 404, 403 y módulo en desarrollo | F4 | Navegación real y pruebas; API conserva JSON y códigos propios | Pendiente |
| 25-06 | 200/201/204/400/401/403/404/429/500 | F2/F3/F5 | Casos positivos/negativos y fallo inyectado solo en prueba; 204 sin cuerpo | Casos API probados F2/F3, 409 adicional y 500 seguro sin ruta pública de fallo; revisión F5 pendiente |
| 25-07 | CRUD categorías y cajas | F2/F3/F4 | Crear/leer/editar/borrar con roles, FK coherentes, validaciones y pruebas cruzadas | REST probado F3; interfaz conectada F4 pendiente |
| 25-08 | Variables de entorno | F1/F5 | .env.example ficticio, secretos ignorados, config por entorno y arranque comprobado | Implementado y comprobado localmente F1; revisión final F5 pendiente |
| 25-09 | Hash de contraseñas | F2 | Valor almacenado distinto al original y check_password correcto | PBKDF2-SHA256 y validadores probados con hashing real |
| 25-10 | Pruebas unitarias | F2/F3/F5 | pytest y pytest-django; resultados reales y nombres de pruebas trazables | 146 casos aprobados (67 base F2 + 79 F3); validación final F5 pendiente |
| 25-11 | PostgreSQL y migraciones | F1/F2/F3/F5 | Conexión real, base desde cero, migraciones versionadas y sin cambios pendientes | F2 y CHECK de estados/prioridades F3 aplicados; User 0001 sin auth_user; base test desde cero y sin pendientes |
| 25-12 | Diagrama ER editable | F0/F2/F5 | Fuente Mermaid contrastada con modelos/migraciones reales | Actualizado al núcleo real F2, futuro separado; renderizado Mermaid no verificado; revisión F5 pendiente |
| 25-13 | Carga inicial 50–100 usuarios | F5 | CSV e informe: usuarios alcanzados, spawn, duración, RPS, media, p95 y fallos | Pendiente; ninguna carga ejecutada |

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
| T-09 | Interfaz española y responsive | F4: escritorio/móvil, teclado y estados de error/carga | Pendiente |
| T-10 | HTTPS, CORS, secretos, red privada | F1 configuración; F5 preparación; despliegue/F7 verificación externa | Pendiente |
| T-11 | No depender ni sobrescribir Android/VPS | F0: no hay fuentes originales; API propia planificada | Restricción respetada; compatibilidad no verificada |
| T-12 | Git y commits por fase, sin secretos | F1 en adelante: diff e historial local; nunca push implícito | Historial local por fase; sin remoto/push; secretos y artefactos ignorados |
| T-13 | Salud de servicio | F1: respuesta y conectividad DB; 503 si dependencia falla | Comprobado: 200 con DB, 503 al detenerla y recuperación posterior |
| T-14 | Datos demo identificados y controlados | F2/F5: comando/fixtures limitados y guion explícito | Pendiente |
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
