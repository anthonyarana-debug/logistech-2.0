# Presupuesto F7 — revisión previa a cualquier recurso

Consulta: 28/10/2026. USD, tarifas de referencia antes de impuestos, sobreconsumos y
variaciones regionales. **No se creó ningún recurso ni se consumieron créditos AWS.**

## Cuenta y dominio

Datos confirmados por el usuario en Console: Free Plan activo, US$100 restantes,
183 días, vencimiento28/04/2027, región us-east-2 Ohio. No se accedió a la cuenta:
no hay CLI/perfil/conector AWS configurado aquí. Elegibilidad y cuotas concretas
se deberán confirmar en su selector antes de Crear, sin aceptar un upgrade.

stackpe.online está registrado en Porkbun según el usuario, vence05/05/2027.
Destino acordado: https://logistech.stackpe.online. Consulta DNS de solo lectura
confirmó NS de Porkbun; no se confirmó registro A del subdominio. No se modificó DNS.

## Servicios disponibles en Free Plan

La documentación actual de la nueva experiencia AWS incluye **EC2 y Lightsail**
entre servicios Free Tier. Lightsail sustituyó sus pruebas antiguas por créditos
Free Tier. Esto permite evaluarlo con el saldo, sin prometer que un bundle concreto
esté habilitado en esta cuenta. Si la consola solicita Paid Plan, detenerse y
revisar la alternativa; no convertir el plan. [Lista AWS](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html),
[créditos Lightsail](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html).

EC2 enumera para cuentas nuevas t3.micro/t3.small/t4g.micro/t4g.small/c7i-flex.large/
m7i-flex.large. **t3.medium no se propone como elegible.** c7i-flex.large ofrece4GiB
pero consume bastante más crédito; t3.small ofrece2GiB y requiere más cuidado de RAM.
[Elegibilidad EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html).

## Comparación de arquitectura, 730h/mes

| Alternativa | Cómputo/mes | Disco/IPv4/transferencia | Base estimada | US$100 sin extras |
|---|---:|---|---:|---:|
| Lightsail Linux2GB,2vCPU |12.00|60GB SSD, IPv4 de bundle,3TB incluidos|12.00|8.33 meses teóricos; manda vencimiento del plan |
| **Lightsail Linux4GB,2vCPU** |**24.00**|80GB SSD, IPv4 de bundle,4TB incluidos|**24.00**|**4.17 meses** |
| EC2 t3.small2GiB |15.18 aprox.|gp3 40GB3.20 + IPv43.65; salida según cuota|22.03 aprox.|4.54 meses |
| EC2 c7i-flex.large4GiB |61.90 aprox.|gp3 40GB3.20 + IPv43.65|68.75 aprox.|1.45 meses |

Lightsail: precios publicados vigentes, IP estática sin cargo adicional mientras
está asociada; fuera de asociación prolongada puede costar0.005/h. [Bundles](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bundles.html).

EC2: valores de cálculo0.0208/h y0.0848/h y gp3 0.08/GB-mes son **hipótesis de
estimación**, pendientes de cotización exacta en Ohio antes de autorizar. No se
presentan como tarifa regional confirmada. IPv4 sí tiene referencia pública0.005/h;
100GB de salida gratuita son cuota agregada, no ilimitada. T3 se prepara en modo
CPU credits standard para evitar recargo unlimited. [EC2](https://aws.amazon.com/ec2/pricing/on-demand/),
[IPv4](https://aws.amazon.com/vpc/pricing/), [EBS](https://aws.amazon.com/ebs/pricing/).

## Recomendación y recursos exactos

Recomendar **una Lightsail Linux4GB en Ohio**, condicionada a selector/creditos de
la cuenta. Tiene margen para Django+PostgreSQL+proxy, mantenimiento y siguientes
fases. Alternativa2GB cuesta la mitad: solo para equipo pequeño, imágenes compiladas
fuera del servidor y vigilancia de RAM; no se certificó capacidad de carga AWS.
En ensayo local el uso en reposo fue aproximadamente48MiB PostgreSQL,131MiB Gunicorn
y12MiB proxy, excluyendo sistema operativo, Docker y picos: no sirve como garantía
para dimensionar únicamente por esos valores.

Recursos iniciales de plantilla: **1 instancia +1 IP estática asociada**. Se necesita
una clave SSH regional existente o importación pública previamente aprobada, y SSH
limitado al /32 del administrador. React estático, Gunicorn, PostgreSQL privado y
throttle compartido viven como contenedores en la misma VM. DNS permanece Porkbun.
No hay RDS, ALB, NAT Gateway, Route53, Secrets Manager, Redis administrado ni ECR
obligatorios. No se incluye un segundo servidor/alta disponibilidad.

Backups lógicos diarios privados y copia cifrada fuera de AWS: coste AWS adicional0
si se descargan al equipo/vault existente por el canal privado y dentro del bundle.
Opcional: snapshots Lightsail a0.05/GB-mes;80GB-mes serían4.00 y160GB-mes8.00,
pero el uso incremental real varía. **No se habilitan por la plantilla inicial.**
Con reserva de snapshots: **28–32/mes**, unos **3.13–3.57 meses** de US$100.
Presupuesto sin snapshots24/mes, unos4.17 meses. Son duraciones aproximadas y no
promesas de crédito aplicable ni límites automáticos de gasto.

No necesitamos comprar otro dominio, delegar DNS, pagar certificado ni contratar
S3 inicialmente. Un bucket privado podría justificarse después para copias, con
presupuesto separado; S3 en la misma cuenta no protege del bloqueo de todo Free Plan.

## Riesgos del plan y control de consumo

El Free Plan termina al agotar crédito o cumplir su plazo, lo primero. Después
se pierde acceso; AWS retiene contenido90días y su recuperación exige Paid Plan,
que **no está autorizado**. No debe dependerse de esa retención: exportar backups
cifrados y claves de recuperación fuera de AWS antes de la fecha/saldo límite.
No se presupuestan otrosUS$100 potenciales como disponibles. [Condiciones AWS](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html).

Los snapshots, transferencia extra, IPv4 sin asociar y recursos retenidos siguen
consumiendo crédito. Detener Lightsail no detiene su coste; borrar requiere un
procedimiento y autorización distintos. La retención CloudFormation evita pérdida
accidental pero tampoco elimina cargos. Revisar saldo semanalmente y diariamente
si baja deUS$25; acordar copia/salida antes deUS$10, sin borrar automáticamente.
Una alerta de presupuesto no es un tope de facturación. No aceptar acciones como
Organizations/ControlTower que puedan cambiar el plan automáticamente.

## Aprobación aún pendiente

Antes de ejecutar: confirmar Lightsail4GB/Ohio disponible, créditos aplicables,
precio mostrado, clave SSH/CIDR, contacto ACME y autorización del presupuesto
(24/mes base o28–32 si se aprueban snapshots). Solicitar aprobación independiente
para crear recursos y agregar el A de Porkbun. Revisar también hallazgos de seguridad
residuales del informe. No se modificó el plan de cuenta ni se desplegó la URL.
