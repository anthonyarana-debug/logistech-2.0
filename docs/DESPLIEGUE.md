# Ejecución local y preparación futura

Estado F1: Docker Linux local ejecutado y verificado. Cloud no desplegado ni evaluado.

Actualización F2 (2026-10-27): modelos y autenticación migrados/verificados localmente; aplicar migraciones explícitamente como indica README antes de iniciar flujos de autenticación. Ver SEGURIDAD.md y ENDPOINTS.md. La evidencia F1 de este documento se conserva como antecedente.

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
