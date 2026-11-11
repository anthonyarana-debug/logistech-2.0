# Guía de exposición de Semana 13

1. Desde la raíz, abrir Docker Desktop con motor Linux. Configurar los secretos locales siguiendo la [guía F7](AWS_F7_GUIA.md). Ejecutar `pwsh -NoProfile -File scripts/start_week13.ps1` y abrir `https://localhost:8453` con la CA del ensayo confiada.
2. Iniciar sesión con una cuenta de ensayo preparada en privado. Mostrar la diferencia entre superadmin, administrador y operador, y la espera de asignación de un registro público.
3. Abrir Categories, crear una categoría sintética, aplicar un filtro y navegar entre páginas. Mostrar la página 2 de las evidencias si el catálogo actual tiene pocos registros.
4. Abrir Boxes, registrar una caja, consultar su QR en el detalle, buscarla en Identify a box, confirmar su recepción y revisar History.
5. Consultar PostgreSQL con `docker exec logistech-week13-db-1 psql -U logistech_owner -d logistech -c "SELECT count(*) FROM boxes_box"`. Mostrar salud HTTPS con la CA local y los logs con `docker logs --tail 20 logistech-week13-backend-1`.
6. Ejecutar la cantidad solicitada de un perfil acotado con `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/demo_semana13.ps1 -Escenario Paginacion -Cantidad 100`. En PowerShell 7 usar `pwsh -NoProfile -File scripts/demo_semana13.ps1 -Escenario Paginacion -Cantidad 100`. Para paginación están disponibles 100, 500, 1.000, 2.500 y 5.000. Para registro use `-Escenario Registro -Cantidad 2`. Abrir [la gráfica](evidencias/semana13-cierre/capacity.html).
7. En el ensayo sintético, ejecutar `py scripts/verify_week13_recovery.py` para demostrar restauración y persistencia. Programar ese paso fuera de otras operaciones de la demo, ya que reinicia servicios del ensayo.
8. Abrir una ruta inexistente, mostrar la respuesta al acceso de un operador sin empresa y revisar las capturas de 500/503 simulados.
9. Una vez autorizado y publicado, abrir el sitio público, comprobar certificado, salud y los flujos desde otra red. Ver [aceptación AWS](AWS_F7_GUIA.md).

[Preparación local y credenciales de ensayo](LOGISTECH_SEMANA_13_DEMO.md)
