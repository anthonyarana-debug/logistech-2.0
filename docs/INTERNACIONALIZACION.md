# Idioma e internacionalización

Adaptación aprobada después de F5, sin iniciar F6/F7/F8. La documentación permanece en español; la aplicación utiliza inglés por defecto. No hay API externa de traducción ni nuevas dependencias de producción.

Inventario portable de mensajes anteriores y actuales: [INVENTARIO_IDIOMA](INVENTARIO_IDIOMA.md).

## Política y superficies

`frontend/src/i18n/en.js` centraliza el catálogo inglés. `i18n/index.js` proporciona `t(key, values)`, `defaultLocale`, `formatNumber`, `formatDate` y `resultCount`. Las claves nuevas están en inglés y son independientes de campos API. `t` exige claves y argumentos conocidos; no ejecuta HTML, no interpreta valores interpolados recursivamente y React escapa su salida. Las fechas se presentan en inglés y America/Lima; la persistencia UTC no cambia. Números y plurales usan Intl.

Se adaptaron landing/SVG, login, registro, dashboard, navegación, categorías, cajas/detalle/estados, validaciones, vacíos, diálogos, toasts, sesión, health, 403/404, módulo futuro, aria-labels, skip links, título y descripción HTML. `lang=en` coincide con los textos. Preferencias españolas del navegador no cambian el idioma predeterminado. Los mensajes nativos de validación del navegador pertenecen al navegador y pueden seguir su idioma; las ayudas y validaciones propias son inglesas.

Django configura `LANGUAGE_CODE=en` y conserva `USE_I18N=True`. Los mensajes propios API se centralizan en `backend/apps/core/messages.py`; Django/DRF aportan mensajes ingleses de framework. No se habilita negociación por Accept-Language. `labels.py`, `admin_presentation.py`, filtros y dos plantillas Admin traducen etiquetas, choices y errores conocidos en presentación, sin cambiar modelos o migraciones. Las plantillas adaptan únicamente etiquetas/encabezados de Django 5.2 y mantienen su estructura y licencia BSD.

El comando create_demo también utiliza ayuda, validaciones y confirmación inglesas centralizadas; conserva los nombres y descripciones DEMO españoles como datos de negocio.

## Español opcional

Esta entrega prepara la extensión, pero **no habilita un segundo idioma incompleto**: no hay selector español ni afirmación de paridad bilingüe. Para incorporarlo correctamente, añadir un catálogo `es` completo con las mismas claves/placeholders, pluralización y formatos; un proveedor reactivo para todas las vistas y constantes derivadas; gettext/catálogos backend y negociación explícita coherente. Probar ambos idiomas y sus ayudas accesibles antes de ofrecer el selector. La documentación técnica y los datos de negocio pueden estar en español desde ahora.

## Contrato y datos que se conservan

No cambian rutas web o `/api/v1/`, nombres de campos, enums, permisos, filtros, códigos HTTP, cookies o JWT. Las claves `detalle`, `errores`, `campos`, `filtros`, `estado`, `servicio`, `base_de_datos` y los valores de salud `disponible`/`no_disponible` son contrato legado y se conservan. El texto humano de error es inglés; los clientes deben decidir por código HTTP y campos, no comparando frases traducibles.

Se conservan `CJ-`, internal_id automático, QR independiente, roles SUPERADMIN/COMPANY_ADMIN/OPERATOR, estados REGISTERED/RECEIVED/REJECTED y prioridades LOW/NORMAL/HIGH. No se traducen nombres/descripciones de usuarios, empresas, productos, categorías, sucursales o datos DEMO persistidos. `LEGACY_DOMAIN_MESSAGES` solo reconoce mensajes de validación exactos generados por el modelo para la presentación de Admin; no aplica reemplazos a los valores de negocio. Los verbose_name/choices históricos permanecen en los modelos; Options se copia para renderizar el Admin. No se requiere migración por idioma.

## Seguridad y verificación

JWT en memoria, refresh HttpOnly, CSRF, aislamiento por empresa, restricciones PostgreSQL, bloqueo transaccional, rate limiting y errores 500 seguros se mantienen. El HTML de etiquetas Admin se escapa salvo que ya sea una etiqueta confiable de Django; hay prueba específica contra entrada HTML no confiable.

Pruebas: `backend/tests/test_language.py`, `frontend/unit/i18n.test.js`, `frontend/e2e/language.spec.js` y regresiones existentes con selectores ingleses. Resultados reales y limitaciones en [INFORME_ADAPTACION](INFORME_ADAPTACION.md); evidencia nueva separada de F0–F5. Los informes históricos conservan sus textos/capturas españoles. No confundir el catálogo con una traducción de datos almacenados.
