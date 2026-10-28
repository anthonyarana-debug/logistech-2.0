# Resumen de consolidación del informe académico

Fecha: 28 de octubre de 2026 (America/Lima).

## Entrega

- Word editable: `documents/INFORME_LOGISTECH_2_0_CONSOLIDADO.docx`.
- PDF de presentación: `pdf/INFORME_LOGISTECH_2_0_CONSOLIDADO.pdf`.
- 35 páginas A4, 12 tablas y 10 figuras numeradas. Las figuras 2 y 4 tienen continuaciones para facilitar su lectura. El logo de portada no se cuenta como figura académica.

## Elementos conservados de la versión de la compañera

Se trabajó sobre una copia del documento original, conservando su portada institucional, logo TECSUP, curso, proyecto, semestre, docente, ubicación, periodo y organización de contenidos. Se mantienen los tres índices separados, la tipografía Times New Roman, el cuerpo mayoritariamente a doble espacio y el tratamiento APA de tablas con líneas horizontales.

Los cuatro integrantes se conservaron exactamente como figuran en la portada:

1. Arana Apaza, Anthony Fernando.
2. Mamani Puma, Anyelina Yolit.
3. Quispe Romero, Katherine Melany.
4. Robles Uscamayta, Alexandra.

Se preservaron las seis tablas del cuerpo, incluido el checklist de semana 11, y el esquema general de arquitectura. Se adaptó Carta a A4 por solicitud expresa; el título de portada se distribuye en dos líneas para respetar el ancho útil.

## Selección de diagramas

| Sección | Selección | Motivo y tratamiento |
| --- | --- | --- |
| Arquitectura, Figura 1 | PNG original incorporado en el documento base, 2045 × 652 px | Su composición conceptual resulta más clara que la pequeña vista modular del informe técnico anterior. Se conservó el archivo sin re-encodificar y se ajustó al ancho de A4. La tabla de módulos mantiene el detalle de core y demás responsabilidades. |
| Modelo, Figura 2 | SVG técnico original `fase5-modelo-datos.svg`, derivado de `MODELO_DATOS.mmd` | Incluye los atributos y cardinalidades, la empresa opcional del usuario y los identificadores independientes. Se renderizó a 2600 × 4474 px; no se extrajo del PDF. Se agregó una continuación con los atributos y claves a mayor tamaño, construida a partir del mismo archivo fuente, sin modificar modelos. |
| Sesión, Figura 3 | SVG técnico original `adaptacion-sesion.svg` | La secuencia representa CSRF, access en memoria, cookie HttpOnly, rotación y revocación. Se renderizó a 2600 × 2066 px, sin extraer imágenes pequeñas del PDF. |
| Autorización, Figura 4 | Flujo técnico original `PROCESOS.mmd` | Se distribuyó en dos paneles legibles: identidad/ámbito y autorización/escritura. Conserva 401/403/404, actor y empresa, pertenencia, transacciones, validaciones y resultados; no introduce operaciones nuevas. |
| Interfaz y Locust, Figuras 5–10 | Capturas reales ya documentadas | Se trasladaron las imágenes originales con sus notas, conservando proporciones. No se generaron pantallas ficticias ni resultados nuevos. |

## Evidencias incorporadas del informe técnico

El Anexo A ocupa las páginas 22–33. Describe herramienta, objetivo, configuración, procedimiento, evidencia, resultado e interpretación. Incluye la salida literal recuperada de pytest y las capturas de navegador y de los reportes HTML de Locust; la salida literal no se presenta como una captura de terminal.

- pytest: 163 aprobadas, 15.66 s, PostgreSQL real, fuente E01.
- Playwright: 10 casos aprobados, cero fallos u omisiones; tabla de casos y duraciones, fuente E02.
- Unitarias Node: se reutiliza E19, ocho aprobadas con mocks. Se aclara que el paso Docker que descubrió cero pruebas no acredita ese resultado. La recuperación Node se ejecutó en la preparación documental anterior, no durante esta consolidación.
- Locust con 50 usuarios: 4161 solicitudes, media 14.44 ms, p95 22 ms, 23.19 solicitudes/s y cero fallos HTTP.
- Locust con 100 usuarios: 8368 solicitudes, media 19.23 ms, p95 38 ms, 46.37 solicitudes/s y cero fallos HTTP.
- Se preservan la incidencia del escritor CSV de Locust al cierre, las diferencias entre snapshots y resultados finales, las regresiones iniciales y sus límites de interpretación.
- k6 se identifica como herramienta propuesta inicialmente, sin ejecución ni resultados atribuidos.
- Cloud continúa parcial, sin afirmar despliegue inexistente.

## Correcciones y comprobaciones

1. Capítulos correlativos 1–11: procesos pasa a 7, API a 8, resultados a 9, referencias a 10 y conclusiones a 11. El apartado repetido de indicadores pasa a 9.2. El anexo usa A.1–A.7.
2. Se reconstruyeron los tres índices con campos nativos de Word y se actualizaron sus páginas. General: p. 2; tablas: p. 3; figuras: p. 4.
3. Tablas del anexo renumeradas 7–12 y referencias internas corregidas. Figuras 1–10 con títulos y notas, sin duplicar las continuaciones en el índice.
4. Tablas ajustadas al ancho útil A4, anchos por columna, interlineado compacto dentro de celdas, filas completas y cabeceras repetibles. La comprobación nativa de Word confirma que cada una de las doce tablas comienza y termina en la misma página.
5. Se redujeron saltos y espacios innecesarios, y se ajustó la secuencia de autenticación y la autorización para evitar páginas casi vacías. Se reservan páginas para diagramas y capturas extensos cuando es necesario para su lectura.
6. Referencias ampliadas y notas de procedencia. Exactamente cinco conclusiones numeradas constituyen el último apartado, en p. 35.
7. PDF exportado con Microsoft Word; las 35 páginas renderizadas se revisaron visualmente. Se verificaron A4, ausencia de campos rotos y concordancia de índices.
8. SHA-256 de los dos documentos Word de entrada y las veinte fuentes primarias contrastados sin cambios. Los PNG del logo y la arquitectura originales permanecen presentes sin re-encodificación.

No se ejecutaron nuevas pruebas del programa en esta consolidación. No se modificaron código, permisos, base de datos, infraestructura, repositorio Android ni GitHub. No se sobrescribieron los documentos originales ni se realizaron commits, push o despliegues.
