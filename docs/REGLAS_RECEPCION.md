# Reglas F6, Bloque 2 — definidas antes de la integración

Una caja nace REGISTERED. RECEIVED significa recepción aceptada y REJECTED recepción
rechazada: son estados finales, como en F3. Una recepción persistente vincula caja,
empresa, sucursal, actor, fecha y resultado. No calcula ni incrementa stock.

1. Solo una caja REGISTERED puede resolverse una vez, como RECEIVED o REJECTED.
   La sucursal debe coincidir con la de la caja; no hay traslado implícito.
2. Empresa, producto, categoría y sucursal deben ser coherentes; empresa, producto
   y sucursal activos. Rechazo requiere DAMAGED, INCORRECT_ITEM u OTHER; aceptación
   no admite motivo. No se almacenan notas libres ni información sensible en eventos.
3. OPERATOR/COMPANY_ADMIN activos operan solo en su empresa activa; SUPERADMIN
   válido puede operar globalmente. User.branch continúa organizativa, no una nueva
   ACL por sucursal. Usuario pendiente no recibe ni consulta inventario privado.
4. POST /receipts/ exige Idempotency-Key UUID. Se limita por actor y empresa. El
   reintento de la misma solicitud devuelve el registro original (200); nueva
   recepción 201; reutilización para otra solicitud o caja ya resuelta 409. Otro
   actor no obtiene una recepción mediante la clave de un tercero.
5. Actor, caja, empresa y referencias se bloquean dentro de la transacción.
   Receipt, estado y evento se confirman juntos o se revierten juntos. Unicidad
   PostgreSQL por caja y por actor/empresa/clave respalda el bloqueo.
6. PATCH/PUT antiguos que resuelven REGISTERED mantienen su contrato y pasan por
   el mismo servicio, con origen BOX_STATUS_UPDATE. Rechazo antiguo sin campo de
   motivo se registra como OTHER, sin atribuir una causa desconocida. No se añade
   un requisito de cabecera al contrato antiguo. Repetir el mismo estado final
   no crea otra recepción. Clientes nuevos deben usar /receipts/ e idempotencia.
7. Cajas terminales anteriores conservan estado/IDs: no se inventa fecha, actor ni
   recepción histórica. Historial nuevo empieza en las operaciones instrumentadas.
8. Eventos se añaden con snapshots de UUID de caja, referencia legible y datos
   permitidos. Sin FK que impida el borrado permitido de una caja REGISTERED:
   BOX_DELETED y su historia sobreviven. Las recepciones sí protegen su caja.
9. Historial/recepciones son inmutables por API, ORM y triggers UPDATE/DELETE de
   PostgreSQL. No es un registro criptográficamente inviolable frente al dueño de
   la base: superusuarios pueden alterar esquema o truncar tablas. Backups y
   permisos de operación siguen siendo necesarios.
10. QR contiene solo logistech:box:<qr_code>. UUID de modelo, internal_id y qr_code
    continúan independientes; conocer cualquiera no concede acceso. Resolución,
    imágenes y etiquetas requieren autenticación y ámbito empresarial del servidor.
