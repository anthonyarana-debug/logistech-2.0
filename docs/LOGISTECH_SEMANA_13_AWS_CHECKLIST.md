# Checklist AWS de Semana 13

## Verificado localmente

- [x] CloudFormation pasó cfn-lint para el candidato F7.
- [x] Gunicorn, Caddy y PostgreSQL pasaron el ensayo aislado con HTTPS y origen único.
- [x] Base privada, rechazo CORS, persistencia, backup, cifrado autenticado, restauración y rollback ensayados.
- [x] Trivy registró 0 CRITICAL y 48 HIGH residuales. La evaluación técnica de los HIGH sigue pendiente antes de publicar.

## Cuenta y aprobación

- [ ] Confirmar en la consola Lightsail de Ohio que el Free Plan permite crear el bundle Linux IPv4 de 4 GB, 2 vCPU, 80 GB y 4 TB. El precio de lista es US$24/mes. Si AWS admite el uso de créditos para el bundle y no hay otros cargos, US$100 cubrirían aproximadamente 4,17 meses, sujeto al vencimiento y consumo real. Confirmar la IP estática, transferencia excedente y snapshots por separado. [Planes Lightsail](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bundles.html)
- [ ] Confirmar permisos de lectura en cuenta y Lightsail. Consultas opcionales con AWS CLI autenticada y sin exponer credenciales:

  ```powershell
  aws lightsail get-regions --region us-east-2 --include-availability-zones
  aws lightsail get-bundles --region us-east-2
  aws lightsail get-blueprints --region us-east-2
  ```

- [ ] Obtener aprobación explícita para instancia, IP, cargos y cambio DNS. Resolver los HIGH o registrar aceptación técnica de los riesgos por componente.

## Ejecución y verificación una vez aprobadas

1. Seguir la [guía F7](AWS_F7_GUIA.md) en us-east-2. Asociar IPv4 estática. Restringir SSH a la IP autorizada y publicar únicamente 80/443. Verificar el estado y los puertos antes de dirigir tráfico.
2. Identificar la revisión completa mediante `git rev-parse HEAD`, usarla en `SOURCE_REF` y comprobar los digests de las imágenes. Configurar los secretos fuera de Git y migrar siguiendo la guía.
3. Crear el registro A `logistech.stackpe.online` en Porkbun hacia la IPv4 aprobada. Comprobar resolución externa y certificado público emitido y renovable por Caddy.
4. Verificar HTTPS, salud, login, roles, aislamiento, QR, recepción e historial desde fuera del host. Configurar retención de logs, alertas y backup cifrado fuera de la instancia.
5. Conservar el SHA anterior, imágenes y dump verificado. Revertir a las imágenes anteriores únicamente con un esquema compatible. Si requiere restauración, usar una base separada, verificar el manifiesto y conmutar tráfico tras comprobar salud y autenticación. Conservar el volumen anterior.

Cuenta, cuotas, gasto y DNS quedan pendientes. No se aprovisionaron recursos ni se publicaron cambios remotos.
