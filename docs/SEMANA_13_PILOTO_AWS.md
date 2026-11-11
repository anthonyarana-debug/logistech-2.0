# Piloto de aceptación en AWS

El piloto de escritura requiere aprobación específica para dos empresas sintéticas con un identificador común de ejecución, cuentas temporales y datos de inventario ficticios. Su alcance excluye cuentas y datos existentes. Se registra el SHA ejecutado, la hora y los estados HTTP sin conservar secretos ni contenido de cuentas reales.

1. Con SUPERADMIN, crear dos empresas y sus sucursales. Crear un COMPANY_ADMIN para la primera y operadores asignados a ambas. Confirmar listado, detalle y actualización de cada entidad dentro de su alcance.
2. Con COMPANY_ADMIN, crear categoría y producto de prueba. Confirmar que puede administrar su catálogo y que no puede consultar inventario de la segunda empresa. Verificar 403 para ámbito prohibido y 404 para detalle ajeno.
3. Con OPERATOR, registrar una caja autorizada y consultar el identificador y QR. Resolver la etiqueta y comprobar que el operador de la otra empresa no puede verla. Confirmar que el operador no administra categorías ni elimina cajas.
4. Registrar recepción mediante el contrato de idempotencia. Comprobar estado, consulta de historial y rechazo de una segunda recepción con distinta clave. Conservar la caja recibida y su historial.
5. Probar borrado solo con referencias sintéticas sin dependencias. Desactivar las cuentas temporales y registrar los identificadores de las entidades que deban conservarse por trazabilidad. Mantener los datos del piloto identificados.

Hasta contar con autorización, usar Playwright y PostgreSQL de ensayo para cubrir estas operaciones. [Guía de exposición](SEMANA_13_GUIA_EXPOSICION.md)
