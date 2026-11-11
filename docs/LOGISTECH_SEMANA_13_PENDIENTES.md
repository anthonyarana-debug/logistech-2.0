# Pendientes de Semana 13

- **Despliegue público.** Confirmar elegibilidad actual de la cuenta y autorizar recursos, gasto y DNS. El ensayo está disponible en `https://localhost:8453`. Se conserva la preparación F7. [Guía AWS](AWS_F7_GUIA.md)
- **Capacidad.** El mayor perfil que cumplió el criterio fue 5.000 GET con 20 VU y p95 de 39.94 ms. Los perfiles 10.000–50.000 están preparados en k6 y fuera del rango habilitado por el runner local. Requieren entorno dedicado, presupuesto de cuotas y escalamiento sostenido. La política de registro limita las altas a tres por hora por IP.
- **Referencias y paginación.** Los clientes antiguos conservan el listado sin envoltorio. Los selectores de referencias siguen usando su contrato anterior. Medir catálogos masivos antes de migrar estos clientes y definir cuándo retirar el listado completo.
- **Monitoreo.** CPU y memoria de carga se capturaron antes y después. Se registró una serie temporal de espacio en disco y EXPLAIN de dos páginas. Queda instrumentar CPU, RAM y consultas durante operación sostenida. Definir un RPO y RTO para la operación real y medirlos fuera del portátil.
- **Revisión operativa.** Revisar alertas HIGH residuales, advertencias HSTS, rotación de copias y verificación pública del certificado. Mantener el repositorio de respaldo como punto de retorno y desplegar por SHA e imágenes auditadas.

## Preparación para aprobar el despliegue

El candidato sigue siendo una instancia Linux Lightsail en Ohio, 2 vCPU, 4 GB, 80 GB, IPv4 y precio de lista de US$24 mensuales. Confirmar la cotización de la cuenta, créditos aplicables, vigencia, costo de la IP estática y almacenamiento de snapshots antes de provisionar. [Planes Lightsail](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bundles.html)

| Paso | Permiso o decisión | Riesgo y verificación posterior |
|---|---|---|
| Revisar plan y región | Lectura de cuenta, facturación y planes Lightsail | Confirmar Ohio, Linux y costo |
| Instancia, IP y firewall | Aprobar gasto e IAM para crear instancia, asignar y asociar IP y gestionar puertos | Restringir SSH al operador. Abrir 80/443. Comprobar que PostgreSQL y Gunicorn solo usan sus redes privadas |
| Preparar host y contenedores | Acceso SSH del operador y secretos entregados por canal privado | Verificar SHA, imágenes, espacio, variables, migración y checks antes de recibir tráfico |
| DNS y certificado | Autorización separada para el A de logistech.stackpe.online en Porkbun | Verificar resolución, renovación ACME y HTTPS público |
| Aceptación | Operador de la aplicación y entorno de datos autorizado | Comprobar salud, login, roles, CORS, backup fuera de instancia y monitoreo |

Para rollback, conservar el SHA y las imágenes anteriores junto con el dump verificado. Antes de modificar esquema o datos, probar la restauración en otro volumen. Si falla el release, revertir primero el tráfico y volver al conjunto de imágenes y base compatibles. Conservar el volumen fallido para inspección. [Procedimiento F7](AWS_F7_GUIA.md)
