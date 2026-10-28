# Base de datos — esquema vigente F6

## F6, Bloque 2 — nuevas entidades y migraciones

boxes.0003_boxevent_receipt crea Receipt y BoxEvent sin rellenar procedencias históricas. boxes.0004_immutable_reception_history instala triggers PostgreSQL que rechazan UPDATE/DELETE; reversión de esquema existe para entornos de pruebas, no debe usarse como rutina destructiva.

Receipt: UUID, company/branch/actor PROTECT, box OneToOne PROTECT, internal_id snapshot, result/reason/source con CHECK, idempotency_key UUID y UNIQUE(company,actor,key), created_at; índice (company,created_at). BoxEvent: UUID, company/branch/actor PROTECT, box UUID snapshot sin FK, internal_id, event_type/outcome con CHECK, data JSON acotado/permitido, created_at; índice (company,box,created_at). No hay saldo de stock nuevo.

Los FK simples no prueban igualdad de empresa entre tablas: servicio y modelos conservan esa responsabilidad. Eventos son append-only en API/ORM y protegidos por triggers contra modificación/borrado ordinarios; dueño de DB/TRUNCATE o alteración de esquema no quedan criptográficamente impedidos. Una prueba migra F6 bloque1 con cajas REGISTERED/RECEIVED/REJECTED y comprueba IDs/estados intactos y cero recepciones/eventos ficticios.

Migraciones ejecutadas exclusivamente en logistech-f6 aislado; base de trabajo preservada. Revisar backup, restauración, crecimiento de eventos, permisos y ventana de migración antes de aplicar a otro entorno.

## Ampliación vigente F6

Migraciones aditivas: accounts/0002 añade User.branch nullable con FK PROTECT y CHECK branch requiere company; organizations/0002 añade CHECK ACTIVE/INACTIVE para Company/Branch; catalog/0002 añade CHECK ACTIVE/INACTIVE para Product. Las 0001, los UUID, internal_id y qr_code existentes se conservan. Diagrama editable actualizado; SVG/PNG fase5 permanecen evidencia histórica.

Aplicadas únicamente a PostgreSQL aislado logistech-f6. Una prueba transaccional migra datos históricos 0001 al esquema actual y comprueba preservación de usuario, caja, cantidades, identificadores y referencias. Antes de migrar otra base: backup/restauración verificados y revisión de estados/relaciones; los CHECK deben fallar ante datos inválidos, no borrarlos automáticamente. User.branch es asignación organizativa, no nuevo límite de autorización de inventario.

Permanece la limitación de FKs simples: igualdad de empresa entre tablas se valida en modelos y servicios REST con bloqueos; no hay RLS ni triggers de aislamiento. No utilizar bulk/SQL para saltar estas validaciones.

Fecha: 2026-10-27. PostgreSQL 17.11 real, psycopg 3.3.6 y Django ORM. Sin SQLite. Diagrama actual editable: [MODELO_DATOS.mmd](MODELO_DATOS.mmd). La ampliación de F6 queda separada en [MODELO_FUTURO.mmd](MODELO_FUTURO.mmd).

Validación F5: sin migraciones nuevas/pendientes; User permanece en 0001 y auth_user ausente. Introspección de constraints, pertenencia y cantidades sin inconsistencias; columnas de las seis entidades comparadas con el ER sin diferencias en fase5-verificacion.json. ER renderizado e inspeccionado: [SVG](evidencias/fase5-modelo-datos.svg) y [PNG](evidencias/fase5-modelo-datos.png). El diagrama de negocio omite expresamente tablas de framework y relaciones M2M de permisos. PostgreSQL de carga vive en volumen de logistech-f5 separado; no modifica la base principal. TLS verify-full está preparado para producción, pero no conectado a un PostgreSQL cloud real.

## Esquema implementado

| Entidad | Campos y restricciones principales |
|---|---|
| Company | UUID PK, name, status ACTIVE/INACTIVE y created_at |
| Branch | UUID PK, company PROTECT, name, address, status, created_at; nombre único por empresa sin distinguir mayúsculas |
| User | AbstractUser sin username/date_joined; UUID PK, email único y Lower(email) UNIQUE, password hash, first_name/last_name, role, company nullable PROTECT, is_active/is_staff/is_superuser, last_login y created_at; grupos/permisos heredados de Django |
| Category | UUID PK, company PROTECT, nombre único por empresa sin distinguir mayúsculas, descripción, is_fragile/is_perishable independientes y created_at |
| Product | UUID PK, company, category PROTECT, SKU normalizado a mayúsculas único por empresa, nombre, descripción, status y created_at |
| Box | UUID PK, internal_id `CJ-` + UUID hexadecimal independiente, qr_code UUID diferente y UNIQUE, company/product/branch/created_by PROTECT, quantity > 0, weight_kg decimal opcional > 0, priority, status y created_at |

Estados iniciales de caja: REGISTERED, RECEIVED, REJECTED. Prioridades: LOW, NORMAL, HIGH. Son decisiones nuevas, no enums corroborados del Android. F3 implementó validación de estados/transiciones iniciales y CRUD REST; no existe todavía el módulo completo de recepción ni sus eventos.

Constraints de usuario: SUPERADMIN implica is_staff/is_superuser verdaderos y ninguna empresa; OPERATOR/COMPANY_ADMIN no pueden tener is_superuser. COMPANY_ADMIN requiere empresa. is_staff aislado no otorga alcance global ni entrada al Admin restringido.

Constraints DB verificadas: email case-insensitive y flags de privilegio, cantidad positiva de caja y unicidad. Model.full_clean también valida pertenencia de categorías/productos/sucursales/creador a la misma empresa; save lo ejecuta y el Admin usa formularios validados. No se permite cambiar company de un recurso persistido mediante save. El índice de cajas es (company, status, created_at), además de índices de FK y UNIQUE.

**Límite:** FKs simples y CHECK no garantizan igualdad de empresa entre tablas. QuerySet.update, bulk_create o SQL pueden omitir clean/save. Se probaron constraints DB que sí existen, no aislamiento por trigger. F3 debe imponer querysets, servicios transaccionales, validación de FK y permisos en cada endpoint. No usar operaciones masivas para modificar relaciones sin esas validaciones.

## Migraciones

Se generaron cuatro primeras migraciones: organizations/0001_initial, accounts/0001_initial, catalog/0001_initial y boxes/0001_initial, con sus fuentes versionadas. `AUTH_USER_MODEL=accounts.User` estaba configurado antes de ejecutar migrate.

accounts/0001_initial crea User y depende de organizations y de los grupos/permisos de auth. Es normal que el plan de auth.0001 mencione su modelo User histórico: Django lo omite físicamente al estar intercambiado. Se comprobó en PostgreSQL que **accounts_user existe y auth_user no existe**. boxes, Admin y blacklist referencian el usuario intercambiable, sin dependencia de un usuario desechable.

Aplicadas también migraciones oficiales contenttypes/auth/admin/sessions/token_blacklist. `migrate --check` y `makemigrations --check --dry-run` pasan. La suite crea una base PostgreSQL de pruebas desde cero, aplica el grafo y comprueba el modelo en el estado de accounts.0001_initial. No se reescribieron migraciones ya aplicadas ni se eliminó el volumen anterior.

Tablas adicionales de framework: grupos/permisos y relaciones M2M, django_admin_log, django_session, django_content_type, django_migrations, token_blacklist_outstandingtoken/blacklistedtoken. La última mantiene registro de refresh tokens, por lo que la base y sus futuros backups deben tratarse como sensibles; las evidencias no vuelcan estas filas.

## Operación

```powershell
docker compose exec -T backend python manage.py migrate --check
docker compose exec -T backend python manage.py showmigrations
docker compose exec -T backend python -m tools.verificar_base
```

El verificador imprime solo estructura/versiones/estado de migraciones, sin usuarios, contraseñas ni tokens. La prueba HTTP crea una cuenta rotulada de prueba por ejecución y la deja inactiva, sin empresa y con contraseña inutilizable. No genera inventario. El resto de fixtures vive en una base test_ separada y se elimina por pytest.

Para crear superadministrador: `docker compose exec backend python manage.py createsuperuser`; usar el prompt seguro. Asignación posterior de empresa/rol mediante el Admin restringido en `/admin/`, accesible únicamente a superadministradores activos. Sin credenciales fijas ni superadmin automático.

CHECKLIST HUMANO: crear un superadministrador local mediante prompt si se desea revisar la administración; no enviar la contraseña al chat. Restauración/backups y roles PostgreSQL de producción siguen pendientes de fases posteriores.

## Cambios F3

Migración `boxes/0002_box_box_status_allowed_box_box_priority_allowed`: CHECK de status en REGISTERED/RECEIVED/REJECTED y priority en LOW/NORMAL/HIGH. Aplicada al volumen local sin reset ni eliminación de datos; salida real en evidencias/fase3-migraciones.txt. Los tests intentan omitir clean mediante QuerySet.update y PostgreSQL rechaza estados/prioridades no permitidos.

No se alteró la primera migración del Custom User. Se mantienen UNIQUE de identificadores/email, cantidad/peso positivos y PROTECT. Category.clean recorta nombre y rechaza vacío. Box.clean conserva creador histórico y no lo invalida si cambia la asignación del usuario; no admite sustituirlo por save. Reglas transaccionales, búsqueda y autorización del CRUD están documentadas en ENDPOINTS.md.

Las fuentes del diagrama de entidades mantienen sus campos/relaciones; los nuevos CHECK no agregan entidades. La migración no implementa Reception, movimientos o auditoría de F6. F3 no creó datos de negocio permanentes para probar CRUD: el servidor HTTP de pruebas utiliza PostgreSQL test_ separado.
