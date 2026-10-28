# Checklist de seguridad — preparación F7

Revisión local: 28/10/2026. Marcas verificadas corresponden al ensayo, no a AWS.

## Verificado localmente

- [x] Base F6 B2 `118eed3` preservada; `main` no se usa como versión más reciente.
- [x] Producción separada de desarrollo; ensayo con proyecto y volúmenes distintos.
- [x] React compilado y API `/api/v1` del mismo origen, sin localhost en el bundle
  como endpoint de producción. Destino público `logistech.stackpe.online`.
- [x] DEBUG false, hosts explícitos, CSRF HTTPS restringido, cookies Secure/HttpOnly
  según su función; contacto ACME y SHA reales exigidos por preflight.
- [x] Backend y PostgreSQL sin puertos de host; ensayo proxy solo loopback.
- [x] Cabeceras de proxy saneadas; no confiar en X-Forwarded-For aportado por cliente.
- [x] PostgreSQL TLS verify-full, CA explícita y certificado SAN db.
- [x] Gunicorn no root; rol DB de aplicación sin superusuario, CREATEDB, CREATEROLE,
  CREATE de esquema ni TRUNCATE de historia. Migraciones con rol separado.
- [x] Recepciones/eventos mantienen triggers inmutables e integridad multiempresa.
- [x] Rate limiting atómico compartido por workers en PostgreSQL; claves HMAC,
  fallo cerrado, sin restablecer cuotas al reiniciar. Limpieza solo de expirados.
- [x] Capas de aplicación de solo lectura, límites CPU/RAM/pids y logs rotados.
- [x] Secretos por archivos excluidos de Git/contextos de build; claves CA/backup
  offline. No credenciales cloud ni DEMO de ensayo en publicaciones.
- [x] Backup lógico y restauración en base nueva; rechazo a sobrescribir bases;
  prueba de conservación de datos al reemplazar imágenes sobre volumen existente.
- [x] Cifrado autenticado CMS AES-256-GCM y descifrado idéntico; no implica que
  todos los dumps locales estén cifrados ni que exista backup externo programado.
- [x] Auditoría de imágenes conserva todos los HIGH/CRITICAL, incluidos sin parche.
  Workflow GitHub solo manual y sin despliegue; su ejecución remota aún pendiente.

## Hallazgos residuales: publicación retenida

Trivy 0.76.1, base de vulnerabilidades descargada en esta revisión, sin supresiones
ni `--ignore-unfixed`. Son **ocurrencias paquete/CVE**, no número de ataques ni
garantía de explotabilidad. Consultar los JSON completos de `evidencias/fase7`.

| Imagen final ensayada | CRITICAL | HIGH con versión corregida disponible | HIGH sin parche indicado |
|---|---:|---:|---:|
| Backend Python/Django/DRF | 0 | 0 | 44 |
| Proxy Caddy/Go parcheado | 0 | 0 | 1 |
| PostgreSQL Debian actualizado/gosu recompilado | 3 | 0 | 69 |

Se corrigieron dependencias DRF (3.18.3), Go, go-jose v4, x/net y OpenSSL; se
retiraron instaladores Python de la imagen final y se recompiló gosu. No se eliminó
el inventario de paquetes ni se ocultaron alertas para obtener un resultado verde.
`scripts/check_image_vulnerabilities.py` devuelve error por los CRITICAL restantes;
el workflow manual bloquearía esa comprobación. **No declarar lista para Internet
la seguridad de estas imágenes hasta resolver/revisar formalmente esos hallazgos.**

CRITICAL reportados en PostgreSQL:

- **CVE-2025-7458 / libsqlite3-0:** componente del sistema de la imagen, no nuestra
  base de datos ni sustitución de PostgreSQL. Debian bookworm lo mantiene vulnerable;
  la aplicación no ofrece ejecución de SQL SQLite. No equiparar ausencia de una ruta
  conocida con ausencia de riesgo. [Debian](https://security-tracker.debian.org/tracker/CVE-2025-7458).
- **CVE-2026-6653 / libxml2:** Debian bookworm y trixie aún vulnerables, clasificado
  por Debian como incidencia menor aplazada. DB privada y sin endpoint de SQL/XML
  arbitrario reducen exposición; la vulnerabilidad sigue registrada.
  [Debian](https://security-tracker.debian.org/tracker/CVE-2026-6653).
- **CVE-2023-45853 / zlib1g:** Debian indica que contrib/minizip no se compilaba en
  este paquete bookworm y lo marca ignored. Es una discrepancia de aplicabilidad
  documentada, **sin** suprimir el resultado Trivy ni aprobar una excepción automática.
  [Debian](https://security-tracker.debian.org/tracker/CVE-2023-45853).

Los HIGH incluyen componentes de Debian y go-jose v3 transitivo de Caddy sin versión
corregida publicada en el reporte. Requieren revisión del proveedor, superficie y
política de aceptación antes del despliegue. Cambiar de distribución/libxml a mano
solo para alterar el conteo exige verificar compatibilidad PostgreSQL/collation y
restauración; no se hace sobre datos existentes sin una migración probada.

## Pendiente humano y externo

- [ ] Resolver o aceptar formalmente los riesgos residuales con evidencia; repetir
  escaneo con DB actualizada antes de autorizar exposición pública.
- [ ] Confirmar cuenta/plan/cuotas/bundle Ohio y créditos aplicables sin cambiar plan.
- [ ] Autorizar recursos, presupuesto, IP estática y cambio A en Porkbun por separado.
- [ ] Contacto ACME real, clave SSH y CIDR `/32`, SSH por clave, host parcheado.
- [ ] Secretos nuevos para cloud, ACL/lectura correctas, claves offline recuperables.
- [ ] DNS correcto, sin AAAA conflictivo, emisión/renovación TLS públicas comprobadas.
- [ ] Validación desde otra red: certificado, auth, aislamiento y flujo QR/recepción.
- [ ] Backup diario programado, alerta de fallo/antigüedad y copia cifrada externa.
- [ ] Restauración en AWS medida; RPO/RTO y responsables definidos sin SLA inventado.
- [ ] Monitorear créditos, disco/RAM, salud y expiración CA/hoja; salida antes del
  agotamiento Free Plan. Dominio vence después del Free Plan según datos aportados.
- [ ] Revisión final del código/commits; ninguna publicación automática ni gasto.
