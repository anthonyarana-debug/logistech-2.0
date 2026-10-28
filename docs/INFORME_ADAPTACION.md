# Informe de cierre — adaptación de idioma y documentación académica

Fecha: 27 de octubre de 2026, America/Lima. Rama local `codex/documentacion-internacionalizacion`, base `e7e437c1586c887bc096f0e07639598a70306d04`.

**Adaptación completada y verificada localmente para revisión.** No se inició F6/F7/F8. No se hizo push, no se cambió visibilidad en GitHub y no se desplegó infraestructura o aplicación externa. El repositorio ya era público, confirmado por consulta anónima; esta adaptación permanece local hasta autorización de publicación. Cloud continúa **PARCIAL**.

## Alcance entregado

Inglés predeterminado en landing, login, registro, dashboard, navegación, categorías, cajas/detalle, estados/prioridades/roles, formularios, vacíos, confirmaciones, notificaciones, errores, salud y ayudas accesibles. HTML lang/title/description coherentes. Catálogo local frontend de 305 mensajes, interpolaciones y formatos Intl; mensajes/etiquetas API y Admin centralizados, y salida/ayuda inglesa del comando create_demo. Sin API externa ni nuevas dependencias de producción.

Se conservan arquitectura, Industrial Precision, CSS, rutas/campos/enums, JWT/CSRF, permisos, transacciones, rate limiting, restricciones PostgreSQL, internal_id/QR y datos introducidos por usuarios. **Ningún archivo de modelo ni migración fue modificado.** Las claves españolas del protocolo y valores health permanecen por compatibilidad; los textos humanos cambian al inglés.

Español opcional: estructura y procedimiento preparados, pero no se habilita un selector incompleto. Los datos de negocio pueden permanecer españoles; eso no constituye una omisión de traducción. Los mensajes nativos del navegador pertenecen al navegador y pueden seguir su configuración; las ayudas y validaciones propias de aplicación son inglesas.

Documentación nueva: [INFORME_ACADEMICO](INFORME_ACADEMICO.md), [MATRIZ_GUIA_PROFESOR](MATRIZ_GUIA_PROFESOR.md), [API_INTERNA](API_INTERNA.md), [INTERNACIONALIZACION](INTERNACIONALIZACION.md), [INVENTARIO_IDIOMA](INVENTARIO_IDIOMA.md) y fuentes [SESION](SESION.mmd)/[PROCESOS](PROCESOS.mmd). Informe académico español, estructura de la guía y exactamente cinco conclusiones numeradas como último apartado. Autoría académica nominal pendiente de confirmación humana, sin integrantes o contribuciones inventados.

## Verificaciones y resultados reales

| Comprobación | Resultado |
|---|---|
| Base previa de backend | 156 passed, 15.33 s, imagen original y PostgreSQL real aislado |
| Regresión backend ampliada | **163 passed in 15.66s**; 156 anteriores + siete pruebas de idioma/contrato/Admin/datos/escape |
| Unitarias frontend | **8/8**, cinco de sesión conservadas y tres nuevas de idioma/formatos/errores |
| E2E Chromium | **10/10**, dos workers, sin retries; 366.32 s; incluye expiración real de access |
| Inglés por defecto | Navegador es-PE sigue mostrando inglés; lang=en, título, campos, mostrar/ocultar password y salud |
| Accesibilidad y responsive | Axe sin infracciones detectadas en vistas/reglas probadas; teclado/foco/Escape, movimiento reducido y anchos 320/390/768/1440; CSS zoom 200% |
| Django/migraciones | check sin problemas; migrate --check aprobado; makemigrations --check --dry-run sin cambios; Custom User intacto |
| Calidad/dependencias | Ruff, ESLint, build, unitarias y pip check aprobados en contenedores fijados; npm ci local informó cero vulnerabilidades |
| Orquestación | Docker Linux 29.5.3; Compose config --quiet y servicios locales saludables; DB privada |
| Verificador de adaptación | **12/12 comandos con código 0**, sin sobrescribir evidencias F0–F5 |
| GitHub | GET anónimo confirma private=false, visibility=public; solo lectura, sin push |

Evidencias: [baseline](evidencias/adaptacion-baseline.json), [primera regresión ampliada](evidencias/adaptacion-verificacion-inicial.json), [verificación final](evidencias/adaptacion-verificacion.json), [E2E saneado](evidencias/adaptacion-e2e.json) y [visibilidad](evidencias/adaptacion-github-visibilidad.json). Los reportes crudos de Playwright y credenciales DEMO permanecen ignorados; no hay trace/vídeo/storageState. Las interceptaciones 403/500/red siguen declaradas simulaciones; las pruebas backend sí ejercitan permisos/DB reales.

Se inspeccionaron visualmente las capturas nuevas de landing móvil y cajas de escritorio: textos ingleses, composición conservada y datos DEMO españoles sin traducción. No se cambiaron CSS o assets visuales de la aplicación. Se renderizaron y revisaron visualmente los dos diagramas documentales nuevos con Mermaid CLI 12.0.0, disponible en caché local; fuentes editables y SVG/PNG en evidencias. Capturas `adaptacion-landing-*`, `adaptacion-cajas-*` y ampliación CSS se conservan aparte de F5.

## Errores encontrados y corregidos

1. Docker Desktop no estaba iniciado: se inició el motor Linux y se verificó antes de usar PostgreSQL. No se sustituyó por SQLite.
2. La primera regresión ampliada tuvo **162 aprobadas y una fallida**: OPTIONS mostraba display_name como REGISTERED en vez de Registered. DRF requiere una lista de pares al reasignar choices; se corrigió sin cambiar valores de enums. La evidencia fallida se conserva.
3. Se localizaron textos interpolados, SVG, ayudas accesibles, metadatos HTML, mensajes API y etiquetas Admin que una búsqueda solo de tildes habría omitido. Se centralizaron; formularios/Options de Admin se adaptan en presentación, sin migraciones.
4. README negaba carga ya ejecutada; matriz decía sin remoto/push e interfaz española; arquitectura apuntaba a load-tests futuro. Se corrigieron documentos vivos y se preservaron informes F0–F5 como historia.
5. Se corrigió el uso de texto humano como condición de control del cliente health: utiliza un código interno estable de error, conservando el protocolo JSON.
6. Hubo intentos auxiliares de consola con codificación/ruta de npm incorrectas y una primera invocación Ruff sin el config del proyecto; se corrigieron, se revirtieron sus ajustes automáticos ajenos al alcance y se ejecutó Ruff con configuración explícita. No se presentan como pruebas aprobadas.

## Entorno, datos y seguridad

Validación en proyecto `logistech-language`, base/volumen propios, puertos temporales solo loopback 8001/5174 y PostgreSQL sin puerto publicado. Se aplicó el grafo existente desde cero y se generó namespace DEMO propio; el archivo .env.language-demo.json tiene ACL del usuario y está excluido de Git. Los E2E solo modifican esos datos de prueba. No se usó el repositorio Android como remoto ni se modificó su fuente. Las reconstrucciones necesarias aplicaron los cambios de código; no se rebajaron cuotas ni se reiniciaron servicios para convertir fallos 429 en aprobados.

Se ejecuta auditoría nueva de índice e historial antes del commit local; el resultado saneado queda en [adaptacion-secretos.json](evidencias/adaptacion-secretos.json). Comprueba patrones y valores privados locales conocidos y exclusiones; no es certificación absoluta ni OCR de imágenes. Plantillas ficticias permitidas, credenciales reales/DEMO, .env, bases, dumps y volúmenes excluidos. Los datos privados existentes no se borran para hacer pasar la auditoría.

Al terminar se detiene únicamente el proyecto temporal de adaptación, conservando su volumen. No se despliega ni actualiza el stack principal como parte de este ajuste; para revisarlo se puede reconstruir localmente desde esta rama con las instrucciones documentadas.

## Limitaciones y pruebas no ejecutadas

- Sin despliegue cloud, verificación TLS/CA externa, login masivo, capacidad máxima o nuevas mediciones de carga; F5 conserva sus resultados y límites.
- Sin Safari/Firefox, lector de pantalla físico, tacto físico o zoom nativo; no certificación WCAG.
- Español completo opcional no implementado; sin selector que prometa paridad.
- Formato PDF final no generado: se entrega Markdown versionable con ER y fuentes de procesos; la guía usada no exige exportación PDF.
- Auditoría Android/retrocompatibilidad y autoría nominal académica no acreditadas; no se inventan resultados.
- Los 10 E2E validan el frontend adaptado y los flujos API; las ampliaciones finales de presentación Admin/metadata se verifican adicionalmente en las 163 pruebas backend. No se atribuye a Playwright una prueba de navegador Admin que no existe.

## Checklist humano

- [ ] Revisar inglés de interfaz y términos operativos sin cambiar datos de negocio.
- [ ] Revisar informe académico, matriz, API interna y las cinco conclusiones finales.
- [ ] Completar identificación académica nominal y confirmar formato de entrega con el profesor.
- [ ] Mantener cloud marcado parcial y completar verificaciones humanas de accesibilidad si se exigen.
- [ ] Revisar diff y auditoría de secretos considerando que el repositorio es público.
- [ ] Autorizar por separado cualquier push o despliegue futuro; esta entrega no los realiza.

## Comprobación documental

`scripts/check_documentation.py` verifica enlaces relativos de los seis documentos nuevos, cloud parcial explícito y exactamente cinco conclusiones numeradas como último apartado del informe. Resultado en [adaptacion-documentacion.json](evidencias/adaptacion-documentacion.json). Mermaid CLI 12.0.0 renderizó ambos diagramas nuevos a SVG/PNG sin errores; se inspeccionaron sus imágenes.

## Archivos creados o modificados

La lista siguiente incluye código, documentos, pruebas y evidencias de esta adaptación. Los informes y evidencias F0–F5 permanecen intactos.

- `README.md`
- `backend/apps/accounts/managers.py`
- `backend/apps/accounts/permissions.py`
- `backend/apps/accounts/serializers.py`
- `backend/apps/accounts/views.py`
- `backend/apps/boxes/serializers.py`
- `backend/apps/boxes/views.py`
- `backend/apps/catalog/serializers.py`
- `backend/apps/catalog/views.py`
- `backend/apps/core/admin_presentation.py`
- `backend/apps/core/api.py`
- `backend/apps/core/apps.py`
- `backend/apps/core/checks.py`
- `backend/apps/core/errors.py`
- `backend/apps/core/labels.py`
- `backend/apps/core/management/commands/create_demo.py`
- `backend/apps/core/messages.py`
- `backend/apps/core/references.py`
- `backend/apps/core/templates/admin/change_list_results.html`
- `backend/apps/core/templates/admin/includes/fieldset.html`
- `backend/apps/core/templatetags/__init__.py`
- `backend/apps/core/templatetags/english_presentation.py`
- `backend/apps/core/views.py`
- `backend/config/admin.py`
- `backend/config/settings/base.py`
- `backend/config/settings/production.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_crud.py`
- `backend/tests/test_demo.py`
- `backend/tests/test_infrastructure.py`
- `backend/tests/test_language.py`
- `docs/API_INTERNA.md`
- `docs/ARQUITECTURA.md`
- `docs/AUDITORIA_GITHUB.md`
- `docs/DECISIONES_TECNICAS.md`
- `docs/DISENO_UI_UX.md`
- `docs/ENDPOINTS.md`
- `docs/GUIA_DEMOSTRACION.md`
- `docs/INFORME_ACADEMICO.md`
- `docs/INFORME_ADAPTACION.md`
- `docs/INTERNACIONALIZACION.md`
- `docs/INVENTARIO_IDIOMA.md`
- `docs/MATRIZ_ENTREGABLES.md`
- `docs/MATRIZ_GUIA_PROFESOR.md`
- `docs/NUEVA_COMPUTADORA.md`
- `docs/PLAN.md`
- `docs/PROCESOS.mmd`
- `docs/PRUEBAS.md`
- `docs/PUBLICACION_GITHUB.md`
- `docs/SEGURIDAD.md`
- `docs/SESION.mmd`
- `docs/evidencias/adaptacion-baseline.json`
- `docs/evidencias/adaptacion-cajas-1440.png`
- `docs/evidencias/adaptacion-cajas-320.png`
- `docs/evidencias/adaptacion-cajas-390.png`
- `docs/evidencias/adaptacion-cajas-768.png`
- `docs/evidencias/adaptacion-cajas-css-200.png`
- `docs/evidencias/adaptacion-documentacion.json`
- `docs/evidencias/adaptacion-e2e.json`
- `docs/evidencias/adaptacion-github-visibilidad.json`
- `docs/evidencias/adaptacion-landing-1440.png`
- `docs/evidencias/adaptacion-landing-320.png`
- `docs/evidencias/adaptacion-landing-390.png`
- `docs/evidencias/adaptacion-landing-768.png`
- `docs/evidencias/adaptacion-procesos.png`
- `docs/evidencias/adaptacion-procesos.svg`
- `docs/evidencias/adaptacion-secretos.json`
- `docs/evidencias/adaptacion-sesion.png`
- `docs/evidencias/adaptacion-sesion.svg`
- `docs/evidencias/adaptacion-verificacion-inicial.json`
- `docs/evidencias/adaptacion-verificacion.json`
- `docs/licencias/Django-BSD.txt`
- `frontend/e2e/accessibility.spec.js`
- `frontend/e2e/flows.spec.js`
- `frontend/e2e/language.spec.js`
- `frontend/e2e/session.spec.js`
- `frontend/e2e/workspace.js`
- `frontend/index.html`
- `frontend/src/auth.jsx`
- `frontend/src/components/AppShell.jsx`
- `frontend/src/components/ui.jsx`
- `frontend/src/i18n/en.js`
- `frontend/src/i18n/index.js`
- `frontend/src/main.jsx`
- `frontend/src/pages/AuthPage.jsx`
- `frontend/src/pages/BoxDetail.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/pages/Landing.jsx`
- `frontend/src/pages/Resources.jsx`
- `frontend/src/pages/Special.jsx`
- `frontend/src/services/api.js`
- `frontend/src/services/health.js`
- `frontend/unit/i18n.test.js`
- `scripts/check_documentation.py`
- `scripts/verify_adaptation.py`
