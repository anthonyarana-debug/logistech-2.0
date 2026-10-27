# Matriz de requisitos y evidencias

Actualización al cierre de FASE 1 (2026-10-27): base local de Django/React/PostgreSQL/Compose verificada. «Pendiente» conserva el alcance funcional que falta. La fecha objetivo de entrega no fue proporcionada. Evidencias en PRUEBAS.md e INFORME_FASE_1.md.

## Prioridad: entrega del 25 %

| ID | Requisito | Fase responsable | Criterio verificable / evidencia prevista | Estado real |
|---|---|---|---|---|
| 25-01 | Entorno cloud evaluable | F1/F5; despliegue separado autorizado | Configuración, guía, URL autorizada y health comprobado si lo exige la rúbrica | Pendiente; sin cuenta ni recursos verificados |
| 25-02 | Endpoints funcionales y documentados | F2/F3 | Método/ruta/parámetros/auth/respuestas/ejemplos en ENDPOINTS y pruebas HTTP reales | Pendiente |
| 25-03 | Registro y login separados | F2/F4 | Usuario nuevo operador sin empresa, login válido/inválido y flujo web | Pendiente |
| 25-04 | Rate limiting | F2/F3/F5 | Límites documentados, 429 y Retry-After, recuperación de ventana; limitaciones de caché explícitas | Pendiente |
| 25-05 | 404, 403 y módulo en desarrollo | F4 | Navegación real y pruebas; API conserva JSON y códigos propios | Pendiente |
| 25-06 | 200/201/204/400/401/403/404/429/500 | F2/F3/F5 | Casos positivos/negativos y fallo inyectado solo en prueba; 204 sin cuerpo | Pendiente |
| 25-07 | CRUD categorías y cajas | F2/F3/F4 | Crear/leer/editar/borrar con roles, FK coherentes, validaciones y pruebas cruzadas | Pendiente |
| 25-08 | Variables de entorno | F1/F5 | .env.example ficticio, secretos ignorados, config por entorno y arranque comprobado | Implementado y comprobado localmente F1; revisión final F5 pendiente |
| 25-09 | Hash de contraseñas | F2 | Valor almacenado distinto al original y check_password correcto | Pendiente |
| 25-10 | Pruebas unitarias | F2/F3/F5 | pytest y pytest-django; resultados reales y nombres de pruebas trazables | Pendiente |
| 25-11 | PostgreSQL y migraciones | F1/F2/F5 | Conexión real, base desde cero, migraciones versionadas y sin cambios pendientes | PostgreSQL 17.11 conectado; mecanismo migrate sin migraciones F1 comprobado; modelos/migraciones F2 pendientes |
| 25-12 | Diagrama ER editable | F0/F2/F5 | Fuente Mermaid contrastada con modelos/migraciones reales | Diseño conceptual creado; esquema real pendiente |
| 25-13 | Carga inicial 50–100 usuarios | F5 | CSV e informe: usuarios alcanzados, spawn, duración, RPS, media, p95 y fallos | Pendiente; ninguna carga ejecutada |

## Requisitos transversales

| ID | Requisito | Fase / prueba prevista | Estado |
|---|---|---|---|
| T-01 | Backend Django/DRF, React/Vite/JS/Tailwind, PostgreSQL | F1: arranque/build e integración PostgreSQL | Base configurada y comprobada localmente |
| T-02 | JWT mantenido y compatible | F1 selección; F2 emisión/refresh/expiración/revocación según política | Versiones fijadas y smoke criptográfico aprobado; auth de aplicación pendiente F2 |
| T-03 | Tres roles explícitos y mínimo privilegio | F2/F3: matriz en arquitectura trasladada a ROLES_PERMISOS y casos por rol | Diseño propuesto |
| T-04 | Evitar autoasignación y aislamiento entre empresas | F2/F3: dos empresas, lista/detalle/FK, operador sin empresa, flags privilegiados | Diseño propuesto |
| T-05 | Superadmin seguro y flags coherentes | F2: createsuperuser y formularios/gestores administrativos | Pendiente |
| T-06 | Identificación independiente del QR | F2/F3: UNIQUE, generación automática y consulta por ambos identificadores | Diseño propuesto |
| T-07 | Categorías frágiles y perecederas | F2/F3: flags independientes, validación y persistencia | Pendiente |
| T-08 | Empresas y sucursales | F2 núcleo mínimo; F6 administración completa | Diseño propuesto |
| T-09 | Interfaz española y responsive | F4: escritorio/móvil, teclado y estados de error/carga | Pendiente |
| T-10 | HTTPS, CORS, secretos, red privada | F1 configuración; F5 preparación; despliegue/F7 verificación externa | Pendiente |
| T-11 | No depender ni sobrescribir Android/VPS | F0: no hay fuentes originales; API propia planificada | Restricción respetada; compatibilidad no verificada |
| T-12 | Git y commits por fase, sin secretos | F1 en adelante: diff e historial local; nunca push implícito | Historial local por fase; sin remoto/push; secretos y artefactos ignorados |
| T-13 | Salud de servicio | F1: respuesta y conectividad DB; 503 si dependencia falla | Comprobado: 200 con DB, 503 al detenerla y recuperación posterior |
| T-14 | Datos demo identificados y controlados | F2/F5: comando/fixtures limitados y guion explícito | Pendiente |
| T-15 | Documentación completa en español | F0 cuatro documentos principales; F1–F5 ampliación según PLAN | F0 y documentación de F1 entregadas; contratos/modelos/roles funcionales pendientes |
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
- Revisar y autorizar la FASE 1.
