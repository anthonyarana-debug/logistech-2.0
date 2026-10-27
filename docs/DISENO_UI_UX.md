# LogisTech 2.0 — Industrial Precision

Fecha: 27 de octubre de 2026. Entregable de diseño de Fase 2. **Propuesta, no rediseño implementado.** La interfaz de F1 se conserva; la elección definitiva y su implementación corresponden a F4 con autorización. El backend no depende de Stitch.

## Identidad propia

Idea: una etiqueta logística convertida en lenguaje de interfaz. Dos esquinas de registro enfrentadas delimitan el símbolo; una línea de recorrido conecta origen y destino. Wordmark `LogisTech` con una sola incisión rectangular en la L, no un cubo ni un código de barras decorativo repetido. Geometría original por desarrollar/vectorizar en F4, sin reutilizar marcas ni activos de las referencias.

Tres rasgos comunes: titulares editoriales, datos alineados como una hoja de recepción y señales de trazabilidad discretas (ordinales 01/02/03, guías y etiquetas técnicas). Utilizar esos ordinales para pasos reales, nunca como estadísticas. Una operación principal por contexto. Cada componente puede ser sobrio; la identidad surge del conjunto y de la tipografía, no de añadir adornos a cada tarjeta.

## Investigación realmente realizada

Se abrió cada URL solicitada con navegación web y se inspeccionaron las vistas públicas renderizadas en navegador. Fecha de revisión: 2026-10-27. No se iniciaron sesiones, no se pagó, no se descargaron recursos de terceros para el producto y no se copiaron pantallas completas. Las conclusiones de aplicación siguientes son **inferencias de diseño propias**.

| Fuente y alcance observado | Observación concreta | Principio aplicable / límite |
|---|---|---|
| [SiteInspire](https://www.siteinspire.com/), portada, filtros y miniaturas David McGillivray/Royal Sites Ireland | Navegación contenida, bloque editorial junto a categorías, retícula amplia de dos columnas | Separar discurso y exploración; contraste de escala entre titular y metadatos. No se auditó la interacción de los sitios enlazados |
| [Recent](https://recent.design/), galería pública | Barra lateral, filtros por disciplina y piezas de proporciones distintas; composición con muestras de motion y tipografía | Reservar un elemento distintivo por bloque y agrupar navegación estable. Se observaron piezas visuales, no se midieron sus curvas, tiempos ni rendimiento; no se afirma haber probado sus flujos |
| [Land-book: Product / Runner](https://land-book.com/websites/101534-product-runner) | Vista previa desktop/mobile y desglose público en hero, features, how it works, propuesta de valor, CTA y footer | Explicar producto → proceso → acción. El aviso de cookies cubría parte de la vista; el desglose textual era accesible. No se accedió a recursos Pro ni se copió el estilo o contenido de Runner |
| [Refero](https://refero.design/), portada renderizada | Buscador principal, categorías Web/iOS y pestañas Popular/Inspiration/Onboarding/Workflows | Diseñar por tareas y flujos, no solo pantallas. La extracción textual no devolvió contenido; el navegador sí mostró la portada. No se accedió a flujos internos de autenticación/tablas, por lo que no se presentan como auditados |
| [SaaSFrame: Dashboard](https://www.saasframe.io/categories/dashboard), galería pública | Miniaturas “Search indexes overview” de Moss, “Links filtered by tag” y “Link folders” de Dub; navegación lateral estable, listas y acciones en cabecera | Dar protagonismo a tablas/estado operativo y ubicar acciones junto al recurso. El detalle Forest Admin devolvió 403 en la consulta web; no se inspeccionó ese producto ni funciones premium |

Estas fuentes sirven de referencia conceptual, no prueban usabilidad o accesibilidad de LogisTech. No se conservan sus capturas como activos del proyecto.

## Dos alternativas para elegir

### A — Industrial Precision / Hoja de control (recomendada)

Superficie principal marfil, navegación petróleo y lima restringido a acción principal y estado seleccionado. Titular editorial grande en la landing; en el área de trabajo, una tabla ancha y un lateral contextual de detalle, sin mosaico de tarjetas iguales. Líneas de 1 px, radios pequeños, información alineada y numeración técnica de pasos. Adecuada para lectura prolongada y operación en almacenes iluminados; validar esta hipótesis con usuarios, no asumirla demostrada.

Landing: hero asimétrico 7/5, texto a la izquierda y una etiqueta de caja original a la derecha; después una secuencia horizontal de tres pasos y una muestra de la tabla real cuando exista. Dashboard: sidebar 232 px, contexto empresa/sucursal en cabecera, búsqueda, filtros en una fila y tabla. El detalle se despliega como panel lateral en escritorio y página propia en móvil. Login/registro en superficie clara con una banda lateral de marca y contexto de acceso.

```
┌ LogisTech ─────────────────── Acceder · Crear cuenta ┐
│ Titular editorial             Etiqueta / recorrido  │
│ Explicación + CTA             conceptual original  │
├ 01 Identifica ─── 02 Verifica* ─── 03 Consulta ──────┤
│ Beneficios verificables / vista real del producto   │
└ CTA y pie · *Verificación avanzada prevista para F6 ┘

┌ Empresa / sucursal ───── Buscar ───── Acción real ┐
│ Navegación │ Filtros                            │
│ estable    │ Tabla de cajas        │ Detalle    │
│            │ Estado vacío si no hay datos       │
└────────────┴────────────────────────────────────┘
```

### B — Industrial Precision / Terminal de trazabilidad

Superficies petróleo y verde oscuro, títulos marfil, datos técnicos monoespaciados y trazas lineales. El área de trabajo funciona como un registro de operaciones: filas, selección de una caja y detalle en columna derecha. El lima resalta una sola acción o selección, sin efecto neón. La landing combina un titular vertical compacto con un diagrama de recorrido; el formulario se integra en la composición oscura, con campos de borde visible.

Mayor carácter tecnológico y continuidad con el entorno F1. Exige comprobar fatiga visual, legibilidad en exterior, impresión/exportación y contraste de controles; no supone habilitar un selector de tema ni duplicar el sistema. No utilizar consola falsa, terminal animada ni métricas de actividad inventadas.

```
┌ LogisTech / Terminal ─────────── Cuenta ┐
│ Navegación │ Identificar caja          │
│            │ Campo manual + acción     │
│            ├ Registro operativo ───────┤
│            │ Filas reales │ Detalle    │
│            │ o vacío      │ de caja    │
└────────────┴───────────────────────────┘
```

| Decisión | A / Hoja de control | B / Terminal |
|---|---|---|
| Superficie dominante | Marfil, cabecera oscura | Petróleo, paneles verde oscuro |
| Carácter | Editorial y operacional | Técnico y concentrado |
| Tabla | Líneas horizontales, alto contraste | Registro oscuro con selección lateral |
| Titulares | Sans amplia; acento condensado | Sans compacta y código monoespaciado |
| Riesgo a validar | Espacio excesivo si se amplían márgenes sin criterio | Contraste y uso con mucha luz ambiental |
| Recomendación | Base de implementación propuesta | Alternativa válida si se prefiere mayor presencia oscura |

La elección no se da por aprobada. No se construyen ambos temas en F2. Ver las composiciones conceptuales originales [A](diseno/alternativa-a.svg) y [B](diseno/alternativa-b.svg); son bocetos documentales estáticos, sin operaciones ni datos de negocio.

Verificación de bocetos: XML válido y texto descriptivo accesible. El navegador bloqueó la apertura local file:// por su política de protocolos, y el visor de imágenes disponible no admite SVG. No se afirma haber renderizado esos dos archivos; revisar visualmente antes de implementarlos. No se intentó eludir el bloqueo.

## Tokens y contraste

| Token | Valor | Uso |
|---|---|---|
| brand/petroleum | #101F20 | Navegación, texto principal claro, fondo B |
| brand/forest | #203934 | Paneles oscuros secundarios |
| brand/lime | #C5F278 | Fondo de CTA con texto petróleo, selección |
| surface/ivory | #F4F6F2 | Fondo principal A y texto sobre petróleo |
| text/muted-dark | #8B9A92 | Secundario sobre petróleo; no sobre marfil |
| text/muted-light | #51635B | Secundario sobre marfil |
| border/control-light | #73837A | Borde funcional de inputs sobre marfil |
| feedback/success | #23734B | Texto de éxito sobre marfil |
| feedback/warning | #8A5400 | Advertencia sobre marfil |
| feedback/error | #AD3434 | Error sobre marfil |

El cálculo sRGB de los pares propuestos está en [fase2-contraste.json](evidencias/fase2-contraste.json). Resultados: marfil/petróleo 15.587:1; petróleo/lima 13.194:1; secundario claro/marfil 5.877:1; gris original/petróleo 5.759:1. Gris original/marfil **2.706:1** y lima/marfil **1.181:1**: no se usarán como texto normal. El borde funcional claro tiene 3.674:1; no es un color de texto normal.

Objetivo WCAG AA: texto normal ≥4.5:1 y texto grande ≥3:1; comprobar combinaciones finales, incluyendo hover/error/disabled pertinentes. [Referencia W3C de contraste](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). Estos ratios validan pares, no certifican una interfaz completa. Para fondos forest, opacidades y nuevos estados, recalcular antes de implementar.

Tipografía: stack de sistema en F2, sin descargas. Para F4 se propone IBM Plex Sans para cuerpo, Sans Condensed para titulares puntuales y Mono para identificadores, con WOFF2 autoalojadas solo tras revisar licencia/subconjuntos; alternativa sin fuentes externas: system-ui + ui-monospace. Cuerpo 16/24 px, tabla 14/21 px, labels 14/20 px, metadatos secundarios mínimos 13/18 px; títulos 24/30, 32/38 y hero fluido 40–72 px. Pesos 400/500/600. Nunca reducir una tabla hasta hacerla ilegible. Cifras tabulares y código copiable con salto de línea controlado.

Escala espacial: 4, 8, 12, 16, 24, 32, 48, 64 y 96 px. Grid de escritorio 12 columnas, gutter 24 px, máximo 1440 px; tablet 8/20 y móvil 4/16. Márgenes de página 16/24/40 según ancho. Filas de tabla 48–56 px; targets táctiles preferidos 44×44 px o mayores. La recomendación 44 es de producto; [WCAG 2.2 AA establece 24×24 con excepciones](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).

Radios 4 px en controles, 8 px en paneles, píldoras solo para estados breves. Bordes 1 px; focus de 2 px con separación 2 px y contraste sobre el fondo real. Una sombra moderada solo para overlays; no blur de fondo ni elevación decorativa en cada bloque.

## Componentes previstos para F4

| Componente | Variantes/estados | Comportamiento y accesibilidad |
|---|---|---|
| Button | Primario, secundario, texto, peligro; hover/focus/pressed/loading/disabled | Una acción dominante; carga conserva ancho y etiqueta; impedir envíos duplicados, aria-busy |
| Field | Texto, email, contraseña, select; default/focus/error/disabled | Label permanente, ayuda y error asociados con aria-describedby; errores junto al campo y resumen enfocable |
| PasswordField | Visible/oculto, error | Botón con nombre accesible; permitir pegar y gestores de contraseña; no borrar datos al fallar |
| Table | Vacía/cargando/error/con filas/selección | Caption, encabezados semánticos, orden/filtro anunciados; acciones con nombre de recurso; no solo hover |
| Badge | Registrada, recibida, rechazada; frágil/perecedera | Texto además de color; no reutilizar color de estado para clasificar mercancía |
| AppShell | Sidebar escritorio, drawer móvil | Enlace saltar contenido, aria-current; no ocultar cambio de empresa/sucursal |
| FilterBar | Búsqueda y filtros activos | Etiquetas y limpiar filtros; debounce 250–350 ms cuando haya endpoint real; cancelación de petición previa |
| EmptyState | Sin registros/sin resultados/sin asignación | Distinguir causas; proponer solo acciones autorizadas y existentes |
| ErrorState | 403/404/API caída/token expirado | Mensaje claro, reintento idempotente y salida; no mostrar tracebacks ni tokens |
| Dialog/Drawer | Detalle/confirmación | Foco inicial y restaurado, Escape, navegación por teclado; confirmar acciones destructivas según reglas reales |

Iconos: trazos de 1.5–2 px, caja 20/24 px y una familia coherente (propia o con licencia revisada). Siempre acompañar acciones poco familiares con texto. Sin biblioteca adicional hasta comprobar qué componentes la necesitan.

## Organización de pantallas y permisos

Landing: navegación → hero → presentación original/real del producto → flujo logístico → funciones disponibles y futuras diferenciadas → beneficios verificables → CTA → pie. No logos de clientes, porcentajes, ahorros o cifras sin evidencia.

Registro/login: formularios separados, mensajes del backend, estados de carga y aviso explícito de que el registro crea operador sin empresa. No ofrecer elegir rol o empresa. Cuenta sin asignación: explicar espera administrativa, mostrar identidad propia y salida; no inventar inventario ni solicitudes de acceso inexistentes.

Dashboard F4: contexto y acciones permitidas, búsqueda/filtros de categorías/cajas reales, tabla y estados. Solo mostrar indicadores calculados desde endpoints disponibles. Operador: operaciones permitidas; administrador: supervisión de su empresa; superadmin: contexto global inequívoco. Historial, recepción y estadísticas avanzadas permanecen en F6; en F4 solo una vista informativa de módulo en desarrollo si se incluye navegación a ellos.

Móvil: <640 px una columna y navegación en drawer; 640–1023 px paneles apilados; ≥1024 px sidebar y detalle lateral. Tabla con región de desplazamiento identificada o filas adaptadas conservando encabezados accesibles; no desbordar el documento completo. Consulta manual de CJ siempre disponible cuando se implemente. Cámara/QR: espacio y flujo planificados, sin activar permisos o controles falsos en F2/F4.

## Interacciones, accesibilidad y rendimiento

Transiciones de color/opacidad 120–180 ms; apertura de drawer ≤200 ms; evitar animar layout, grandes sombras y filtros. Respetar prefers-reduced-motion y no usar animaciones automáticas de fondo. Estas duraciones son decisiones propias; no mediciones de las referencias.

Operable por teclado, foco visible/no oculto por cabeceras, landmarks y títulos jerárquicos. Validar zoom 200 % y reflujo a 320 px, contraste de todos los estados, lectores de pantalla en formularios y mensajes aria-live discretos. Usar tamaños táctiles cómodos y no depender del color. Error 403 distingue rol insuficiente de sesión expirada; API caída no elimina datos del formulario. Una maqueta no acredita accesibilidad: comprobarlo en F4.

Presupuestos propuestos para F4, aún no medidos: JS inicial gzip ≤200 kB por ruta con separación de carga si es necesaria; CSS gzip ≤30 kB; sin vídeo hero; imágenes futuras en formatos eficientes y dimensiones explícitas; máximo dos familias/pesos imprescindibles con font-display swap. Objetivos de campo LCP ≤2.5 s, INP ≤200 ms y CLS ≤0.1, a medir con entorno/dispositivo identificados. No se afirma que F1/F2 ya los cumpla.

## Brief listo para Google Stitch

Crear propuestas visuales originales de LogisTech 2.0, en español, con dirección Industrial Precision. Generar versiones comparables A (hoja de control marfil con navegación petróleo) y B (terminal de trazabilidad oscura); usar la paleta y componentes anteriores. Preparar landing, registro, login, cuenta sin asignación, dashboard con tabla de cajas y error de servicio, en escritorio y móvil. Identidad basada en esquinas de registro/recorridos; no copiar marcas o pantallas de referencias. Usar placeholders claramente rotulados “sin datos” o “maqueta conceptual”, sin estadísticas ficticias. Mostrar estados vacíos, validación y foco. No agregar funciones ni roles que la API no tenga; recepción/cámara/QR avanzado se describen como futuros. Entregar tokens, medidas y variantes de componentes; no integrar código directamente ni manejar secretos.

No se envió información a Stitch ni se generaron propuestas allí. El usuario puede utilizar este brief; no bloquea el backend.

## Plan de implementación F4

1. Elegir A/B y validar las composiciones con el usuario antes del rediseño.
2. Convertir tokens a CSS/Tailwind y verificar contrastes/estados; revisar licencias antes de autoalojar fuentes o iconos.
3. Construir shell y componentes accesibles; integrar registro/login con CSRF, cookie HttpOnly y access en memoria.
4. Conectar categorías/cajas a endpoints de F3; errores, vacíos, permiso y expiración reales.
5. Probar 320/390/768/1440 px, teclado, zoom, lector de pantalla y rendimiento; registrar evidencia y ajustar.

CHECKLIST HUMANO: elegir A o B antes de autorizar el rediseño en F4; opcionalmente generar y revisar variantes en Stitch con este documento, sin compartir secretos.
