# Fase 6 Bloque 1 Administración operativa

## Base y recuperación

El fetch de origin no mostró cambios nuevos en main: e7e437c. La rama local de
internacionalización añadía d2a160b, 03901ce y 02a1207. Se preservó la entrega
documental pendiente con d5a1fab antes de crear codex/fase-6-administracion.
Ninguna rama histórica fue eliminada. Main conserva su referencia estable.

## Contrato del bloque

- Reutilizar Company, Branch, Category, Product y User. Rutas nuevas /api/v1/.
- SUPERADMIN: empresas y administración global; asigna OPERATOR/COMPANY_ADMIN.
  La API operativa no crea ni concede SUPERADMIN, staff, grupos o permisos Django.
- COMPANY_ADMIN: sucursales, productos y categorías propios; administra solo
  operadores de su empresa. No reclama usuarios pendientes ni cambia roles/empresa.
- OPERATOR: lectura empresarial de sucursales/productos/categorías, cajas según
  permisos F3. Sin acceso al directorio de usuarios ni empresas.
- User.branch opcional, PROTECT, misma empresa y activa al asignar. Es sucursal
  organizativa, no una nueva frontera de autorización del inventario. Los perfiles
  existentes conservan branch=NULL y su alcance de empresa.
- Recursos empresariales no se transfieren. Usuarios: cambio de empresa reservado
  al superadmin, con sucursal coherente; creador histórico de cajas permanece.
- Usuarios se desactivan, no se borran. Superadmins y cambios de privilegios sobre
  uno mismo quedan protegidos. Dependencias impiden borrados de catálogo/empresas.
- Dashboard con recuentos reales según rol, sin stock ni series históricas ficticias.
- Textos nuevos centralizados en inglés; componentes Industrial Precision existentes.

## Secuencia y registro

1. Recuperación y baseline PostgreSQL; preservar documentación.
2. Pruebas API negativas/positivas antes de implementar administración.
3. Migraciones aditivas, API y restricciones; regresión PostgreSQL.
4. Pruebas E2E de administración, componentes frontend y paneles por rol.
5. Seguridad, lint, build, unitarias, E2E/axe y revisión final de cambios.
6. Documentación, commits identificables y auditoría antes de publicar solo la rama.

Pruebas y resultados reales se registran en INFORME_FASE_6.md y evidencias/fase6/.
Los resultados previos permanecen sin sobrescribir. No hay despliegue de pago,
eliminación de volúmenes ni cambios al repositorio Android.

## Evolución preparada y todavía no implementada

1. QR: representación gráfica del qr_code independiente, resolver exacto autenticado,
   cámara con entrada manual alternativa; nunca incluir JWT o datos privados en QR.
2. Recepción: Receipt/ReceiptLine, transiciones transaccionales e idempotencia con
   reglas y migraciones explícitas; REGISTERED/RECEIVED/REJECTED conservan F3.
3. Movimientos y existencias: registro inmutable de movimientos por empresa,
   producto y sucursal; saldo derivado y conciliación. Box.quantity no es saldo contable.
4. Auditoría: eventos actor/ámbito/operación con retención y redacción de datos,
   persistidos en la misma transacción; no se llama historial al created_at actual.
5. Analítica: agregados de eventos reales, paginación/exportación y presupuestos
   de consulta; evitar presentar recuentos actuales como tendencias.
6. Android: inspección de fuentes y contrato versionado antes de tocar su repo;
   documentar auth/cookies versus almacenamiento seguro móvil, capacidades y DTO.
7. Cloud: staging PostgreSQL TLS, secretos externos, migraciones como job único,
   frontend compilado/proxy HTTPS, Gunicorn y límites compartidos. Validar costes,
   región, backups/restauración y autorización antes de aprovisionar.

## Cierre del primer bloque (2026-10-28)

Implementación y validación final realizadas sobre el estado conservado de la rama.
216 pytest con PostgreSQL real, 12 unitarias frontend y 13 Playwright completos
superados. Django check, migraciones, introspección, Ruff, pip check, ESLint y Vite
sin errores. Ver INFORME_FASE_6.md y evidencias/fase6/checks.json.
Se corrigieron etiqueta last_name ausente, descubrimiento unit/ en Docker y
conservación de sucursal inactiva al desactivar usuarios. Sin debilitar permisos.
Se conservó main y no se hizo push ni despliegue. Los siguientes bloques siguen
pendientes; este cierre no declara terminada toda la evolución F6.
