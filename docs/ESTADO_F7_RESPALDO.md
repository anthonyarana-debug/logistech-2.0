# Respaldo F7 — trabajo en progreso

28/10/2026. A petición del usuario se **suspendió la investigación AWS y el
despliegue** para priorizar el respaldo íntegro en GitHub. Rama:
`codex/fase-7-despliegue`. `main` y el historial F0–F6 Bloque 2 se conservan.
No se crearon recursos AWS, modificó DNS ni cambió el plan de la cuenta.

## Avance guardado

Se conservan la preparación de producción, documentación y pruebas F7 de
`8642d99` y `d13135b`, además de las correcciones posteriores de PostgreSQL:

| Hallazgo anterior | Componente Debian instalado | Alternativa candidata mantenida |
|---|---|---|
| CVE-2025-7458: overflow SQLite, posible DoS/divulgación con SQL arbitrario | libsqlite3-0 3.40.1-2+deb12u2 | sqlite-libs no instalado; PostgreSQL sigue siendo la DB real |
| CVE-2026-6653: use-after-free al analizar XML, posible DoS | libxml2 2.9.14+dfsg-1.3~deb12u6 | libxml2 2.13.9-r1, Alpine mantenido |
| CVE-2023-45853: overflow MiniZip; aplicabilidad Debian discutida | zlib1g 1:1.2.13.dfsg-1 | zlib 1.3.2-r1 |

Imagen oficial PostgreSQL **17.11-alpine3.23**, digest fijado, paquetes actualizados
y gosu1.20 recompilado con Go1.27.3. Nuevo clúster/volumen separado con ICU und y
UTF8; **no** se reutilizó físicamente el volumen Debian. Se agregó una protección
que rechaza directorios existentes sin marcador compatible antes de arrancar DB.
No escribir ese marcador a mano sobre datos Debian: migrar con dump/restore a
volumen nuevo. Para volver a Debian, conservar imagen/configuración y volumen
anteriores del commit `d13135b`; nunca compartir PGDATA entre ambas plataformas.

Fuentes del análisis: [SQLite/Debian](https://security-tracker.debian.org/tracker/CVE-2025-7458),
[libxml2/Debian](https://security-tracker.debian.org/tracker/CVE-2026-6653),
[zlib/Debian](https://security-tracker.debian.org/tracker/CVE-2023-45853).

## Resultados reales ya disponibles

- Trivy0.76.1 sin supresiones, mismo alcance HIGH/CRITICAL: PostgreSQL candidato
  **0 CRITICAL/0 HIGH**. Backend0C/44H sin parche indicado; proxy0C/1H sin parche
  indicado. El gate de imágenes pasa, pero quedan45 alertas HIGH para revisión.
- Restauración lógica de un dump Debian actualizado a una base Alpine nueva:
  manifiestos de **8 modelos idénticos**, TLS verify-full, rol runtime limitado,
  triggers activos y pertenencia empresa válida.
- Regresión sobre PostgreSQL Alpine: **307 pruebas aprobadas,33.93s**.
- Playwright completo sobre React compilado/Gunicorn/HTTPS: **8/8 aprobados,5.3min**.
- Verificador local: **10 checks aprobados**, migraciones aplicadas/sin cambios
  pendientes; mantiene2 warnings HSTS documentados en el informe anterior.
- Guard de plataforma: rechaza dos directorios sintéticos incompatibles, sin
  montar volúmenes reales. Frontend lint aprobado.
- Backup nuevo desde Alpine creado correctamente. Ensayo anterior de backup y
  restauración F7 conservado. **Segunda restauración de este nuevo dump Alpine
  aún pendiente** al suspender trabajo para respaldar; no declararla ejecutada.

Evidencias: `docs/evidencias/fase7-seguridad/`. Los logs de presentación normalizan
solo espacios finales/finales de línea. Dumps, secretos, archivos `.env`, cuentas
DEMO y claves permanecen privados/ignorados; no se publican.

## Pendientes para reanudar

1. Completar la segunda restauración y comprobación de persistencia de la imagen
   candidata; finalizar guía de migración/rollback y aceptación de riesgos HIGH.
2. Integrar los resultados nuevos en los documentos de cierre. Los informes F7
   anteriores conservan los3 CRITICAL iniciales como antecedente; este documento
   registra el estado posterior, sin reescribir evidencias históricas.
3. Retomar la cotización/eligibilidad Lightsail en la cuenta ya autenticada, sin
   crear recursos. Se verificaron US$100 y vencimiento28/04/2027 en Console; aún no
   se completó la revisión del bundle de creación. El catálogo público Ohio fue
   recuperado, pero no prueba por sí solo elegibilidad específica de la cuenta.
4. Obtener autorización explícita de recursos/costos y DNS antes de cualquier
   despliegue. No se aprobó exposición pública ni cambio a Paid Plan.

**Estado: F7 WIP, respaldada para continuar; no lista para producción ni desplegada.**
