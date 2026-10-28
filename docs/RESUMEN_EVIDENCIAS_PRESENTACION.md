# Resumen de evidencias para la presentación

Entrega preparada el 27 de octubre de 2026, America/Lima. Informe principal actualizado y exportado a Word/PDF, 29 páginas, 10 tablas y 10 figuras con APA 7 adaptado. Las cinco conclusiones numeradas siguen siendo el último apartado.

## Resultados incorporados

| Herramienta | Resultado | Fuente |
|---|---|---|
| pytest con PostgreSQL real | 163 aprobadas en 15.66 s | adaptacion-verificacion.json |
| Playwright con Chromium | 10 aprobadas, sin retries; 366.32 s | adaptacion-e2e.json |
| axe y responsive | Caso de accesibilidad aprobado; anchos 320/390/768/1440 y CSS zoom | JSON E2E y capturas existentes |
| Locust, 50 usuarios | Media 14.44 ms; p95 22 ms; 23.19 RPS; 4 161 solicitudes; 0 fallos HTTP | Eventos finales y HTML original A |
| Locust, 100 usuarios | Media 19.23 ms; p95 38 ms; 46.37 RPS; 8 368 solicitudes; 0 fallos HTTP | Eventos finales y HTML original B |
| Node unitario local | 8 aprobadas, 315.28 ms; mocks sin base de datos | presentacion/unitarias-frontend-recuperacion.json |
| Grafana k6 | No localizado en las comprobaciones locales; no ejecutado | presentacion/k6-disponibilidad.json |

No se repitieron pytest, Playwright o Locust. Las nuevas capturas muestran los reportes HTML originales de Locust abiertos sin acceso de red, no nuevas cargas. pytest se documenta mediante su salida literal real; no se fabricó una captura de terminal. Se conservaron los originales, incluidas incidencias.

## Corrección probatoria

El paso Node dentro del contenedor guardado anteriormente informó código 0 pero cero pruebas. No acredita ocho aprobaciones. Se documenta la discrepancia y se conserva el archivo: únicamente se ejecutaron las ocho unitarias locales para obtener una evidencia válida persistida. No se cambiaron scripts de pruebas, permisos, modelos, datos o infraestructura para hacerlo.

## Localización rápida en el PDF

- Páginas 16–18: alcance, pytest y casos Playwright.
- Páginas 19–20: capturas reales de interfaz/responsive.
- Páginas 21–22: procedimiento y tablas Locust.
- Páginas 23–24: capturas de reportes originales Locust.
- Páginas 25–27: incidencias, k6 y trazabilidad de las fuentes.
- Página 29: cinco conclusiones finales.

## Archivos de entrega

- output/documents/INFORME_ACADEMICO_FINAL.docx: editable con figuras incrustadas.
- output/pdf/INFORME_ACADEMICO_FINAL.pdf: versión exportada con Microsoft Word y revisada página a página.
- output/ENTREGA_LOGISTECH_2_0.zip: informe, anexo, resumen y fuentes documentales con manifiesto SHA-256.
- docs/ANEXO_PRUEBAS.md: anexo editable separado, también integrado en el informe académico.
- docs/evidencias/presentacion/manifest-evidencias.json: rutas, tamaños y hashes de veinte fuentes, más comprobaciones finales de entrega.

## Límites para explicar al profesor

Cloud sigue parcial, sin despliegue activo. Las cargas son locales, con un login HTTP por escenario y otros JWT de fixtures; no son cien logins simultáneos ni navegadores. La excepción del escritor CSV al cerrar A/B se conserva y no se confunde con fallos HTTP. Los snapshots CSV anteriores tienen 18/8 solicitudes menos que los cierres; se usan los eventos finales contrastados. No se atribuye ninguna métrica a k6. La revisión automática de accesibilidad no sustituye pruebas humanas o certificación WCAG.

Completar la identificación académica nominal antes de presentar; no se inventaron integrantes, docentes, contribuciones o porcentajes de autoría. No hubo push, despliegue, inicio de servicios o modificación de la base de trabajo. Los únicos cambios fuera de documentos son dos utilidades de exportación documental y la exclusión Git de vistas de revisión.
