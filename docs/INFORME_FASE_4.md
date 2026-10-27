# Informe de Fase 4 — Frontend funcional y UI/UX

Fecha: 27 de octubre de 2026, America/Lima. Rama local: `codex/fase-4-frontend`.

**Alcance funcional implementado y comprobaciones disponibles aprobadas. Se entrega para revisión humana. F5 no iniciada. No se declara completo el 25 % ni un despliegue cloud.** Permanecen revisiones humanas de zoom nativo, lector de pantalla y dispositivos físicos; se detallan abajo.

## Verificación previa y entorno

Se comprobó Git limpio en `7e9b7b9` antes de modificar fuentes, se inspeccionaron endpoints, migraciones, permisos, diseño y dependencias reales. La regresión F3 se volvió a ejecutar sobre PostgreSQL: **146 passed en 14.15 s**. Se conservó la arquitectura y se trabajó en rama nueva; sin modificar el original Android, que sigue sin estar disponible para auditoría.

Docker Desktop Linux, PostgreSQL 17.11, Python 3.13.17/Django 5.2.18/DRF 3.16.1/SimpleJWT 5.5.1 existentes; Node 24.19.0 y dependencias fijadas. Backend y frontend en contenedores aislados; Node local para unitarias y Playwright con node_modules del proyecto. No se utilizó Python/Django global ni SQLite.

## Funcionalidades entregadas

- Landing original: navegación, hero, proceso de clasificación/identificación/consulta, beneficios, funciones actuales/futuras, registro/login y pie. Sin cifras de negocio inventadas.
- Login y registro separados conectados a REST, validación, confirmación de contraseña, visibilidad opcional, carga y errores españoles. Registro crea operador sin empresa mediante el servidor.
- Sesión con access solo en memoria, CSRF, refresh HttpOnly existente, restauración al recargar, renovación única ante 401, expiración y logout real. Logout concurrente no restaura identidad; un fallo de red informa cierre no confirmado y conserva solo marcador no secreto para reintentar.
- AppShell con sidebar, cabecera, identidad, empresa, menú móvil y selector de ámbito solo para superadmin. Cuenta sin empresa no consulta inventarios privados.
- Dashboard con conteos de las respuestas actuales y cinco registros recientes; ámbito y límites explícitos, sin presentar unidades de stock ni métricas históricas.
- Categorías: lista, búsqueda, fragilidad/perecibilidad, creación/edición administrativa y eliminación confirmada; errores de integridad visibles. Operador solo lectura.
- Cajas: registro con selectores legibles, lista, búsqueda general/ID interno/QR exactos, filtros de estado/prioridad, detalle completo, edición permitida, marcas recibida/rechazada confirmadas y eliminación administrativa de registradas. Los estados finales quedan protegidos. IDs y creador los asigna el servidor.
- Vistas de acceso denegado, ruta inexistente, servicio, módulo futuro, asignación pendiente y sesión expirada. `/estado` consulta health real; errores privados se muestran sin contenido interno.
- Única ampliación REST: GET `/api/v1/references/` con aislamiento empresarial, actividad y validación de filtros. Sin CRUD nuevo de empresas/productos/sucursales ni migraciones nuevas.
- Procedimiento `create_demo`: dos empresas identificadas DEMO, referencias y cuatro usuarios con claves aleatorias; archivo exclusivo y sin sobrescritura. README documenta preparación y restricciones. La copia local `.env.demo.json` está ignorada y su ACL se restringió al usuario actual. No se imprime ni versiona su contenido.

## Decisión visual y componentes

Alternativa A, Industrial Precision / Hoja de control, con marca oscura de B; un solo sistema. Marfil/petróleo/verde/lima, composición editorial, tablas y líneas contenidas. Ilustración y SVG propios; IBM Plex Sans/Mono autoalojadas con SIL OFL 1.1 conservada en `licencias/`. Sin biblioteca grande de UI, temas duplicados o activos copiados de galerías.

Componentes compartidos: AppShell/Sidebar/Header, Button, FormField, PasswordField, SelectField, DataTable, SearchBar, FilterBar, StatusBadge, Modal/ConfirmModal, EmptyState, LoadingState, ErrorState y Toast. Dialog nativo gestiona fondo/foco/Escape; campos se conservan ante error y el estado de envío impide doble submit. Enlaces de filas incluyen identidad del recurso.

Detalle de caja en página propia tanto móvil como escritorio, para conservar URL directa y espacio legible para identificadores. La investigación histórica de referencias se conserva en DISENO_UI_UX.md; no se afirma acceso a flujos premium ni se copiaron diseños completos. No se utilizó Stitch.

## Archivos creados o modificados

| Área | Archivos |
|---|---|
| Backend mínimo | `backend/config/urls.py`; nuevos `apps/core/references.py`, `apps/core/management/__init__.py`, `management/commands/__init__.py`, `management/commands/create_demo.py` |
| Pruebas backend | `backend/tests/test_references.py`, `test_demo.py` |
| Arranque/estilo frontend | `frontend/src/main.jsx`, `styles/index.css`, `index.html`, `package.json`, `package-lock.json`, `eslint.config.js`, `.prettierrc.json`, `.dockerignore` |
| Sesión/consultas | `frontend/src/auth.jsx`, `services/api.js`, `services/health.js`, `hooks/useRemote.js` |
| Componentes | `frontend/src/components/ui.jsx`, `AppShell.jsx` |
| Pantallas | `frontend/src/pages/Landing.jsx`, `AuthPage.jsx`, `Dashboard.jsx`, `Resources.jsx`, `BoxDetail.jsx`, `Special.jsx`; retirada la pantalla de entorno F1, cuya consulta de salud ahora vive en `/estado` |
| Pruebas frontend | `frontend/playwright.config.js`, `e2e/workspace.js`, `flows.spec.js`, `session.spec.js`, `accessibility.spec.js`, `unit/session.test.js` |
| Verificación | `scripts/verificar_fase4.py`, `resumir_e2e_fase4.py`; `.gitignore` para artefactos privados de pruebas |
| Documentación | README, ENDPOINTS, PRUEBAS, SEGURIDAD, DISENO_UI_UX, MATRIZ_ENTREGABLES, PLAN, DECISIONES_TECNICAS, este informe, licencias y evidencias F4 |

Los paths abreviados en una misma fila son relativos al directorio indicado. No se cambiaron modelos/migraciones/permisos CRUD existentes ni Compose/puertos para acomodar el frontend. Fontsource es dependencia de ejecución; Playwright 1.64.1 y axe-core/playwright 4.14.0 son de desarrollo. Todas fijadas en lockfile.

## Pruebas ejecutadas y evidencia

| Comprobación | Resultado real |
|---|---|
| Regresión inicial F3 | 146 passed, 14.15 s, PostgreSQL |
| Suite backend final | **151 passed, 16.18 s**, PostgreSQL desde migraciones |
| Checks Django y migraciones | Sin problemas, sin cambios de modelo ni migraciones pendientes |
| Dependencias Python y lint | pip check y Ruff aprobados |
| Frontend lint/build/audit | Aprobados; npm audit 0 vulnerabilidades en esa ejecución |
| Unitarias de sesión Node | **5/5**, concurrencia/CSRF/logout/errores |
| E2E Chromium | **9/9 casos**, ocho flujos y una comprobación adicional de accesibilidad, ejecuciones separadas sin retries |
| Ampliación de cobertura final | Landing/ancla, administrador y superadmin se repitieron con éxito; foco visible, módulo futuro, filtros QR/ID/estado/prioridad y cantidad inválida comprobados |
| Responsive | 320/390/768/1440 px, landing/cajas sin overflow del documento; desplazamiento local en tabla |
| Accesibilidad automática | Axe sin infracciones detectadas en las reglas WCAG A/AA ejecutadas sobre vistas seleccionadas; Tab/Escape/foco y movimiento reducido |
| Ampliación | Reflujo con CSS zoom 200% aprobado; zoom nativo no confirmado |
| HTTP a través de proxy | Health 200; categorías/cajas/referencias sin token 401 |
| Infraestructura final | Tres servicios saludables; web/API solo loopback y PostgreSQL sin puerto publicado |

`python scripts/verificar_fase4.py` registró **19 comprobaciones, todas con código 0** en [fase4-verificacion.json](evidencias/fase4-verificacion.json). Nombres/estados/tiempos E2E sin payloads en [fase4-e2e.json](evidencias/fase4-e2e.json). El test de access espera la expiración real de cinco minutos; tardó aproximadamente seis minutos incluyendo límite de login. Dos peticiones simultáneas renovaron una sola vez. La parte de refresh ausente elimina su propia cookie e inyecta un Bearer inválido; no modifica seguridad del servidor.

Tras formatear las fuentes para facilitar mantenimiento/revisión, se reconstruyó solo frontend y se volvieron a aprobar lint, build y cinco unitarias: [fase4-frontend-final.json](evidencias/fase4-frontend-final.json). Landing y accesibilidad se repitieron con éxito sobre esa imagen. El build final registra JS gzip 96.55 kB y CSS gzip 7.36 kB, más las fuentes locales; no son mediciones de red o Web Vitals.

Las pruebas usan dos empresas y roles reales. Los 146 casos F3 siguen cubriendo cruces empresariales, campos prohibidos, unicidad, constraints y rate limiting. F4 añade referencias y demo sin sustituir esa suite. Los E2E usan datos locales DEMO y dejan cajas finales/cuentas `e2e-...@example.test` de prueba identificables; no se ejecutan contra producción.

### Revisión manual separada

Se abrió la web en navegador integrado: revisión visual de landing y login, navegación por ancla Producto tras corregirla, foco por teclado del email a contraseña y revisión de capturas móviles. Se detuvo **realmente** solo el backend mediante Compose: `/app` mostró “No pudimos restaurar tu sesión” y error seguro; se inició de nuevo y “Volver a intentar” llevó al login, sin cookie válida. Servicios recuperados y saludables.

Los E2E de fallo de red y de 403/500 de interfaz usan interceptación explícita. Se distinguen de la caída real manual y de los códigos reales del backend; no prueban disponibilidad histórica ni infraestructura externa.

Capturas verificables:

- [Landing escritorio](evidencias/fase4-landing-1440.png), [320 px](evidencias/fase4-landing-320.png), [390 px](evidencias/fase4-landing-390.png), [768 px](evidencias/fase4-landing-768.png).
- [Cajas escritorio](evidencias/fase4-cajas-1440.png), [320 px](evidencias/fase4-cajas-320.png), [390 px](evidencias/fase4-cajas-390.png), [768 px](evidencias/fase4-cajas-768.png).
- [Ampliación CSS 200%](evidencias/fase4-cajas-css-200.png), [login manual](evidencias/fase4-login-manual.png), [backend realmente detenido](evidencias/fase4-backend-caido-manual.png).
- [Landing final, navegador integrado](evidencias/fase4-landing-manual.png).

Las capturas contienen solo datos académicos identificados; no contraseñas, tokens o cookies. Informes crudos, contextos de error y credenciales demo están ignorados, sin trazas/vídeos/storageState.

## Errores encontrados y correcciones

Primer pase E2E: cinco aprobados y dos fallidos. Uno era una expectativa incorrecta del texto de 404 en la prueba; el otro reveló que el estado de registro exitoso se conservaba al navegar al login. Se corrigieron la prueba y las identidades de los formularios; ambos pasaron después. La inspección manual también detectó que React Router cambiaba el hash sin desplazar la página: se agregó navegación al ancla y se verificó automáticamente y en navegador.

Se corrigieron globals de lint, imports/formato Python, bloqueo de envío en Button, asociación de ayudas y mensajes españoles ante errores de red. Las advertencias NO_COLOR/FORCE_COLOR y de archivo lento de Playwright no representan fallos; se conserva el test largo porque verifica expiración del servidor. No se desactivaron throttles, CSRF, permisos, validadores o constraints para aprobar.

## Limitaciones y pendientes

- No se confirmó zoom nativo 200%: los atajos del navegador integrado no produjeron cambio verificable. Sí se comprobó ampliación CSS/reflujo 200%. Falta lector de pantalla (NVDA/VoiceOver), móvil táctil físico y navegadores distintos de Chromium. No se declara certificación WCAG.
- Selectores/colecciones actuales sin paginación ni virtualización; adecuados para demostración inicial, no evidencia de escala. Conteos dependen de las respuestas existentes.
- No se midieron Web Vitals de campo, carga, capacidad o rendimiento cloud. El build registra tamaños locales, no garantiza latencia real. Throttling sigue LocMem por proceso.
- Compose usa servidores de desarrollo y HTTP loopback. No se desplegó ni modificó infraestructura pública. HTTPS/operación externa requieren autorización y validación futuras.
- La identificación QR se consulta por contenido; no hay imagen escaneable, cámara/OCR, historial, recepciones avanzadas o CRUD completos de organizaciones/productos.
- Datos demo y archivo de claves son locales, no una cuenta de producción; el propietario debe conservarlos de forma privada y decidir su limpieza. No se eliminaron datos de fases previas.

## Checklist humano antes de autorizar F5

- [ ] Revisar landing, login y área operativa en `http://127.0.0.1:5173` y aprobar identidad A con recursos oscuros de B.
- [ ] Consultar credenciales exclusivamente en el archivo local privado y recorrer los cuatro usuarios demo; no enviarlas al chat.
- [ ] Confirmar zoom nativo 200%, NVDA/VoiceOver, foco/errores, contraste percibido y tacto en un dispositivo real.
- [ ] Revisar estados finales, eliminación confirmada, 409 de categoría referenciada y ámbito de superadmin.
- [ ] Revisar evidencias, datos académicos persistidos y limitaciones de despliegue/capacidad.
- [ ] Confirmar rúbrica y requisitos cloud/costos, si aplican; autorizar cualquier despliegue por separado.
- [ ] Autorizar expresamente F5 tras revisar este informe. **No se iniciará automáticamente.**

Preparación para F5: documentación sincronizada, procedimiento demo, verificador, pruebas unitarias/E2E y evidencias disponibles. Carga 50–100 usuarios, evaluación integral del 25% y cloud permanecen en el plan, sin ejecutarse en esta fase.
