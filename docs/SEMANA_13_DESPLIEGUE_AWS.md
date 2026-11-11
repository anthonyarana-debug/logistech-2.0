# Despliegue de LogisTech en AWS

El 11/11/2026 la consola autenticada mostró Free Plan, US$100 de crédito, 170 días restantes y vencimiento el 28/04/2027. En Ohio ofreció Ubuntu 24.04 LTS de doble pila, 2 vCPU, 4 GB de RAM, 80 GB SSD y 4 TB de transferencia por US$24/mes. La autorización se recibió antes de crear la instancia. Si el crédito se aplica al bundle y se mantiene el consumo base, US$100 equivalen a 4,17 meses antes de impuestos, extras y vencimiento. [Tarifas Lightsail](https://aws.amazon.com/lightsail/pricing/)

| Recurso | Estado | Costo de referencia |
|---|---|---:|
| Lightsail logistech-f7 | Activa en us-east-2a | US$24/mes |
| IPv4 logistech-f7-ip | 18.221.197.129, asociada | Incluida mientras permanezca asociada |
| Disco del bundle | 80 GB | Incluido |
| Snapshots | Desactivados | US$0 previsto |
| DNS | Registro A de logistech.stackpe.online en Porkbun | Dominio existente |

La consola mostró el aviso CVE-2026-98432. El host pasó de `7.0.0-1014-aws` a `7.0.0-1017-aws` tras instalar `7.0.0-1017.18~24.04.1` y reiniciar. Se verificó la huella SSH mediante la consola Lightsail y se restringió SSH a una IPv4 /32 y al cliente de AWS. [Aviso Ubuntu](https://ubuntu.com/security/CVE-2026-98432) · [Aviso AWS](https://docs.aws.amazon.com/lightsail/latest/userguide/address-cve-2026-98432.html)

La aplicación candidata corresponde al commit local `d92ecad`. Se transfirieron imágenes auditadas por SSH verificando SHA-256 e ID de imagen. Porkbun guardó el registro A con TTL 600 y Cloudflare DNS resolvió la IPv4 esperada. Caddy obtuvo el certificado de Let’s Encrypt. Desde el equipo operador se comprobó HTTPS con el nombre del sitio y la IPv4 explícita, landing y salud HTTP 200, inicio de sesión administrador, lectura paginada y cierre HTTP 204. El resolvedor local aún conservaba temporalmente la respuesta negativa. Se probó una restauración independiente en AWS y se verificó una copia cifrada fuera de la instancia. El temporizador diario quedó activo. [Guía AWS](AWS_F7_GUIA.md) · [Backup y recuperación](BACKUP_RECUPERACION_F7.md)
