# Ejecución local y preparación futura

## Estado vigente F5

**Cloud PARCIAL: planificado y artefactos preparados parcialmente; no desplegado ni verificado.** Se construyó localmente el target `production` de backend con Gunicorn 26.2.0, sin herramientas de desarrollo; pip check/check-config aprobados. Un contenedor efímero sin puertos publicados comprobó redirección 301 y liveness 200 a través de un proxy local simulado. Readiness devuelve 503 porque la base local no tiene el TLS/CA exigido por `verify-full`: es un fallo cerrado esperado, no una conexión cloud acreditada.

Preparado: build estático React, Dockerfile multietapa, `requirements-production.txt`, `deploy/production.env.example`, settings de producción y procedimientos de esta sección. Falta verificar alojamiento de estáticos/SPA/Admin, proxy real, certificados, PostgreSQL TLS privado, secretos, cuentas/cuotas y límite compartido entre procesos. W005/W021 de HSTS se conservan: no se habilita includeSubDomains/preload sin conocer el dominio completo.

### Arquitectura y recursos a autorizar

Un origen HTTPS para web y `/api/v1/`, proxy autorizado que sirve `frontend/dist`, reenvía a Gunicorn privado (punto inicial 2 workers/2 threads) y entrega estáticos Admin de collectstatic. PostgreSQL accesible solo desde backend, sin 5432 público. No publicar directamente Vite/runserver/Gunicorn. Health liveness separado de readiness PostgreSQL; en producción el proxy debe entregar/sobrescribir X-Forwarded-Proto y no admitir acceso público directo al backend.

AWS Academy es una opción a confirmar, no una cuenta auditada: EC2 para aplicación y PostgreSQL en red privada/RDS si el laboratorio lo permite; otra opción académica es DB en red interna de contenedores con disco persistente y respaldo, con disponibilidad inferior. Se necesitan región, cuotas, almacenamiento, dominio/certificado, secretos y política de backup. Tamaño de máquina y presupuesto se eligen tras confirmar restricciones: los números locales de Locust no dimensionan automáticamente EC2.

### Variables y configuración segura

La plantilla contiene solo marcadores. Generar una SECRET_KEY nueva por entorno, claves de base fuera de Git y un rol de aplicación de mínimo privilegio; separar la identidad de migraciones si corresponde. DEBUG=false, ALLOWED_HOSTS y CSRF_TRUSTED_ORIGINS explícitos con HTTPS, cookies Secure/HttpOnly existentes. Producción fuerza `sslmode=verify-full`; montar CA de confianza mediante DB_SSLROOTCERT y usar hostname que coincida con el certificado. No reutilizar las credenciales DEMO/carga ni sus JWT.

TRUSTED_TLS_PROXY=false por defecto. Activarlo solo después de verificar backend privado y sustitución de cabeceras por proxy conocido; de otro modo se puede falsificar el esquema. Sin proxy confiable habrá redirección HTTPS, no una excepción de seguridad. No habilitar CORS genérico. Los límites actuales LocMem son por proceso, así que antes de evaluar multiworker/cloud debe resolverse un limitador compartido y el origen de IP; `NUM_PROXIES=0` no se cambia sin una topología verificada. Esta limitación impide declarar seguridad distribuida completa.

### Procedimiento de despliegue, aún NO ejecutado

1. Obtener autorización explícita para proveedor, recursos/costos y exposición. Confirmar AWS Academy, permisos EC2/RDS y cuotas con el usuario; nunca solicitar credenciales por chat.
2. Preparar red/firewall: HTTPS público solo en entrada autorizada; SSH restringido o canal administrativo del proveedor; backend y DB privados. Configurar CA, dominio y TLS antes de enviar credenciales.
3. Construir y etiquetar imágenes por commit; usar backend target production y artefactos React compilados. Conservar imagen anterior y digest. No copiar .env al build ni servir el árbol de fuentes.
4. Cargar secretos por gestor/archivo privado, aplicar configuración validada y probar conectividad TLS a PostgreSQL con rol limitado. No imprimir `docker compose config` expandido.
5. Realizar backup verificado antes de migrar; aplicar migraciones explícitas y collectstatic con la versión seleccionada. Desplegar primero en entorno de ensayo autorizado, luego cambiar tráfico.
6. Verificar HTTPS/cookies/CSRF, rutas SPA, estáticos, health 200/503, login/logout, dos empresas, roles, límites distribuidos y logs sin secretos desde una red externa. Solo entonces cambiar “desplegado” a “verificado”.

### Recuperación y rollback

Antes de actualizar: backup PostgreSQL en formato custom, roles necesarios, cifrado y ubicación fuera del contenedor/disco de aplicación; comprobar restore en una base vacía separada. Registrar commit/digest, hora, esquema y conteos. Nunca publicar un dump con usuarios/hashes como evidencia académica compartida. La sintaxis orientativa `pg_dump --format=custom --file=<respaldo_privado> <base>` utiliza autenticación mediante gestor/archivo privado, nunca contraseña en la línea de comandos.

Si falla una versión sin cambios de esquema incompatibles: retirar tráfico, recuperar imagen/config anterior, reiniciar procesos y volver a probar health/funciones. Si las migraciones no permiten reversión segura, restaurar primero en DB separada y validar antes de cambiar conexión; no ejecutar migrate a ciegas hacia atrás ni sobrescribir la única copia. Definir con el profesor/propietario ventana de mantenimiento, RPO/RTO y retención; **no se midieron ni se hizo un restore cloud en F5**.

Referencias técnicas consultadas: [checklist oficial Django 5.2](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) para controles de despliegue; [RDS y VPC](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html) para el aislamiento de red propuesto. No prueban disponibilidad o permisos de un laboratorio concreto. Las secciones F1–F3 siguientes son antecedentes y no describen el frontend actual.

Estado F1: Docker Linux local ejecutado y verificado. Cloud no desplegado ni evaluado.

Actualización F2 (2026-10-27): modelos y autenticación migrados/verificados localmente; aplicar migraciones explícitamente como indica README antes de iniciar flujos de autenticación. Ver SEGURIDAD.md y ENDPOINTS.md. La evidencia F1 de este documento se conserva como antecedente.

Actualización F3: CRUD REST y constraints de estados/prioridades aplicados localmente; ejecutar migrate explícitamente al actualizar desde F2. Ver scripts/verificar_fase3.py y su evidencia. El frontend sigue en F1; no cambió la red ni se inició despliegue. La prueba HTTP CRUD usa servidor efímero/test_ dentro del contenedor, no un puerto publicado o servicio permanente adicional.

## Local

Seguir README para generar `.env`, validar Compose sin imprimir secretos y construir/iniciar los tres servicios. Docker Desktop debe ejecutar contenedores Linux. En esta sesión `docker desktop start` resolvió la ausencia inicial del motor.

La base tiene volumen persistente y no publica 5432 en Windows. Web/API solo son accesibles por loopback. Dentro de la red, Django consulta `db:5432` y Vite reenvía `/api` a `backend:8000`. `health/live/` solo comprueba el proceso; `health/` consulta PostgreSQL y responde 503 si falla. Compose espera salud de sus dependencias al iniciar, pero no reinicia automáticamente toda la cadena ante una caída posterior.

Los contenedores incluyen el código al construir. Reconstruir tras modificaciones. Para detener sin borrar datos: `docker compose stop`. No eliminar volúmenes sin autorización y respaldo apropiado. Cambiar POSTGRES_PASSWORD en `.env` no cambia por sí solo la contraseña de un clúster ya inicializado; realizar una rotación administrativa segura si fuera necesario, sin imprimirla.

## Producción: pendiente

`config.settings.production` separa ajustes y habilita protecciones iniciales, pero el Compose entregado es de desarrollo. No exponerlo directamente a Internet. Aún faltan servidor WSGI/ASGI de producción seleccionado y probado, alojamiento del frontend compilado/estáticos Admin, HTTPS/dominio, proxy confiable, límites compartidos, permisos de base, backups y observabilidad. F2 ya implementó autenticación REST; la interfaz web de registro/login espera F4.

La comprobación `manage.py check --deploy --settings=config.settings.production` se ejecutó: W005 y W021 por no extender HSTS a subdominios ni solicitar preload. Mantener ambas decisiones pendientes hasta conocer todos los hosts; no habilitarlas para ocultar advertencias. No se verificaron TLS, firewall remoto, backup o restauración cloud.

## CHECKLIST HUMANO

- Para revisar F1, abrir la web local y el informe; no se necesita cuenta cloud.
- Antes de F5, confirmar si la rúbrica exige cloud activo y qué recursos ofrece AWS Academy u otro entorno académico.
- Antes de cualquier despliegue, autorizar explícitamente proveedor/recursos, cuotas y costos; configurar secretos directamente en el gestor o herramientas del proveedor, sin enviarlos por chat.
- Confirmar dominio y política de subdominios antes de decidir HSTS/preload.
