# Dominio, DNS y HTTPS — F7

Actualizado: 28 de octubre de 2026. Destino acordado:
**https://logistech.stackpe.online**. Es una dirección prevista, no una URL ya
publicada. El usuario conserva `stackpe.online` en Porkbun; vencimiento comunicado:
5 de mayo de 2027. No se modificaron registros, nameservers ni recursos AWS.

## Configuración preparada

| Componente | Valor previsto |
|---|---|
| `PUBLIC_DOMAIN` / Django `ALLOWED_HOSTS` | `logistech.stackpe.online` |
| `PUBLIC_ORIGIN` / `CSRF_TRUSTED_ORIGINS` | `https://logistech.stackpe.online` |
| Frontend compilado | `/api/v1` relativo al mismo origen |
| Proxy | Caddy; React estático y `/api/` a Gunicorn privado |
| Cookies | Refresh HttpOnly, Secure, SameSite=Lax; CSRF y sesión Secure |
| CORS | No se añade un origen cruzado ni comodín; no hace falta para este diseño |
| PostgreSQL | Red Docker interna, sin puerto publicado, TLS `verify-full` |
| Host público | Solo TCP 80/443; SSH 22 limitado al `/32` del administrador |

`deploy/production.env.example` contiene estos valores públicos. El contacto
`ACME_EMAIL` y el SHA completo de la versión siguen siendo obligatorios: sus
marcadores se rechazan en el preflight real. Nunca colocar claves de Porkbun o AWS
en ese archivo. No necesitamos un token DNS de Porkbun para los desafíos HTTP/TLS
normales de este único subdominio.

## Cambio DNS futuro, únicamente después de aprobarlo

1. Crear la VM y asociar una **IP estática Lightsail**; para EC2, usar Elastic IP.
   No apuntar el DNS a una dirección efímera ni inventar una IP en la documentación.
2. En Porkbun → Domain Management → stackpe.online → DNS Records, revisar/exportar
   los registros existentes. Conservar NS, correo/MX, TXT y otros hosts.
3. Revisar conflictos A/AAAA/CNAME/ALIAS del host `logistech`. Si existen, decidir
   explícitamente su sustitución; no eliminar registros del dominio raíz.
4. Agregar **Type A**, **Host `logistech`**, **Answer la IP estática aprobada**,
   **TTL 600** si el panel lo permite. No introducir `https://`, rutas ni puertos.
5. Verificar resolución autoritativa y pública. Revisar CAA si la CA no puede
   emitir. No publicar AAAA salvo que IPv6 esté configurado y probado de extremo
   a extremo. Mantener la gestión DNS en Porkbun; no contratar Route 53.
6. Arrancar el proxy público con 80/443 accesibles. Caddy obtiene y renueva el
   certificado ACME automáticamente, y redirige HTTP a HTTPS. Comprobar cadena,
   nombre del certificado, fecha y acceso desde otro dispositivo/red.

La renovación necesita DNS correcto, reloj del servidor, salida a la CA y puertos
de validación disponibles. Conservar `caddy_data` y `caddy_config`; no borrar esos
volúmenes en las actualizaciones. Vigilar fallos de renovación y vencimiento con
antelación. El HTTPS de Porkbun para otros productos no sustituye el certificado
que sirve nuestro proxy.

## Ensayo local y alcance de la validación

El override `compose.production-rehearsal.yml` mantiene exclusivamente
`127.0.0.1:8087` y `127.0.0.1:8447`, con `localhost` y CA privada Caddy. No se cambia
el hosts de Windows ni DNS público para simular una publicación. Python verifica
la cadena contra la CA explícita y rechaza la misma URL sin esa CA. Playwright
permite la excepción de CA solo con la bandera de ensayo y hostname `localhost`;
queda prohibida para dominios públicos. La emisión/renovación ACME pública sigue
pendiente de DNS, infraestructura y autorización.

El contexto HTTPS permite solicitar cámara; el soporte real de `BarcodeDetector`
y el permiso dependen del navegador/dispositivo. Se conserva la entrada manual.
HSTS inicial es 3600 segundos, sin `includeSubDomains` ni preload para no imponer
políticas a otros servicios de stackpe.online. Aumentarlo requiere validar la
operación pública primero.

Fuentes consultadas: [Porkbun: subdominios](https://kb.porkbun.com/article/200-how-to-create-a-subdomain),
[edición DNS](https://kb.porkbun.com/article/68-how-to-edit-dns-records),
[Caddy: HTTPS automático y renovación](https://caddyserver.com/docs/automatic-https).
