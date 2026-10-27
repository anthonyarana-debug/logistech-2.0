# Guion de demostración académica

Duración orientativa: 12–15 minutos, más la expiración opcional. Usar solo datos DEMO. **Nunca proyectar credenciales, tokens/cookies o .env reales.** Consultar las cuatro cuentas en el archivo local privado preparado por create_demo; los documentos compartidos no contienen sus valores.

## Preparación privada

1. Iniciar Docker Desktop Linux y ejecutar `docker compose up -d --wait --wait-timeout 120` desde la raíz. Si cambió código, añadir `--build`. No usar servidores de desarrollo en Internet.
2. Confirmar `docker compose ps` y `http://127.0.0.1:5173/api/v1/health/` con 200. El puerto 5432 no está publicado.
3. Preparar cuentas identificadas como root, admin, operator y pending en el archivo local .env.demo.json. Si no existen, seguir README/create_demo con namespace nuevo; no reiniciar claves existentes.
4. Cerrar el editor de credenciales antes de compartir pantalla. Iniciar un contexto de navegador limpio. No abrir DevTools Network con respuestas de autenticación ante el público.
5. Tener este guion, CHECKLIST_SEMANA_11, ENDPOINTS, REPORTE_RENDIMIENTO y el ER a mano. No ejecutar nuevamente la carga durante la exposición salvo que lo soliciten: ya hay CSV reales.

## Secuencia

| Paso / qué abrir | Cuenta | Qué mostrar / resultado esperado | Requisitos y evidencia |
|---|---|---|---|
| 1. `/` y `/estado` | Sin sesión | Industrial Precision, CTA, funciones actuales/futuras; botón Comprobar servicio confirma API/PostgreSQL | 01 local/02/11; health y DESPLIEGUE |
| 2. `/registro` y `/login` | Cuenta nueva de prueba | Formularios separados. Primero confirmación distinta: error sin envío válido. Después clave privada robusta: cuenta de operador creada y pendiente de empresa | 03/08/09; E2E, tests de hash. Máximo 3 registros/hora/IP |
| 3. Entrar con esa cuenta o pending | Operador sin empresa | Aviso de asignación, sin inventarios privados; comprobar asignación y logout | 03/07; caso E2E sin requests privados |
| 4. Entrar al dashboard | Administrador | Empresa/rol visibles; conteos son registros del ámbito, no stock ni estadísticas históricas | 02/07; scope en API y UI |
| 5. Categorías | Administrador | Crear “Exposición” con condiciones; editar; eliminar con confirmación. Intentar eliminar categoría referenciada: conflicto visible sin pérdida de datos | 06/07; test CRUD/409. No borrar datos ajenos a DEMO |
| 6. Cajas | Administrador | Seleccionar producto/SKU y sucursal legibles, cantidad y prioridad. Registrar: ID CJ y QR distintos generados por servidor | 02/07/11; constraints y E2E |
| 7. Buscar y filtrar | Administrador | Copiar ID interno del detalle a búsqueda exacta, luego contenido QR; filtrar estado/prioridad. No hay coincidencias si se combinan filtros incompatibles | 07; E2E búsqueda/filtros |
| 8. Editar y cambiar estado | Administrador | Cantidad 0 rechazada; corregir a valor positivo. Marcar recibida con confirmación: queda final, sin editar/eliminar. Crear otra caja registrada para mostrar DELETE permitido | 06/07; validaciones y estado final |
| 9. Rol operativo | Operador asignado | Puede consultar categorías y registrar/editar cajas autorizadas; no crea categorías ni elimina cajas | 07; autorización servidor test_crud |
| 10. Ámbito global | Superadministrador | Seleccionar otra empresa DEMO por nombre; las referencias/listas corresponden al ámbito. No usar un usuario de carga retirado | 07; tests de dos empresas y E2E superadmin |
| 11. Errores y móvil | Sin sesión o rol apropiado | `/403`, ruta inexistente y Recepciones “en desarrollo”. Reducir ventana: menú y tabla con scroll local. Mostrar que el diseño no ofrece recepción avanzada/cámara | 05/06; capturas 320/390/768/1440 |
| 12. Seguridad y sesión | Usuario demo | Recargar restaura sesión; logout vuelve al login y nueva recarga no la recupera. Si se dispone de cinco minutos, dejar vencer access y continuar; si no, mostrar el caso E2E de expiración real | 03/04; unitarias y E2E de cinco minutos |
| 13. Ingeniería y rendimiento | Documentos | Abrir ER editable + SVG, tabla de 156/5/9 pruebas y CSV 50/100; explicar límites de login, entorno local y cloud pendiente | 01/10/12/13; informe F5 y reporte rendimiento |

Para ilustrar 401 sin revelar JWT: abrir `/api/v1/boxes/` en navegador sin Bearer. Para 400/403/404/409/429/500, preferir los tests y evidencias saneadas. No provocar errores artificiales sobre datos de exposición ni desactivar controles. La simulación de caída/500 en E2E se presenta expresamente como tal; los tests TCP de backend sí ejercitan HTTP real.

## Si algo falla durante la exposición

429: leer Retry-After y esperar. La caché es por proceso; no se promete limitación distribuida. Backend no disponible: comprobar servicios y health; conservar datos, no usar down -v. Error de formulario: corregir sin repetir envíos ciegos. Si no se recupera, mostrar evidencia previa con fecha y explicar que no acredita funcionamiento en ese instante. Cloud no activo: mostrar estado PARCIAL y acciones humanas; no sustituir una URL local por una supuesta URL pública.
