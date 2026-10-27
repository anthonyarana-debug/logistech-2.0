# Roles y permisos — Fase 3

Revalidado en F5: mismas reglas, sin expansión de privilegios. 156 casos backend y 9 E2E aislados cubren cuatro estados de cuenta (los tres roles y operador pendiente), cruces empresariales y campos protegidos. Los usuarios de Locust son operadores de fixtures limitadas, retirados al terminar; no son cuentas de producción. Ver INFORME_FASE_5.md.

El rol de aplicación es explícito: SUPERADMIN, COMPANY_ADMIN y OPERATOR. Los porcentajes académicos no son una política de autorización. Registro público fija OPERATOR/company=null; no asigna empresa automáticamente ni ofrece elegir rol.

| Recurso / acción | Rol autorizado | Restricciones | Prueba / estado |
|---|---|---|---|
| Registro público | Público | CSRF, validación, sin campos extra, solo operador sin empresa | test_registration_hash_and_unassigned_operator; test_registration_rejects_privileged_fields |
| Login | Cuenta activa | Credenciales válidas, CSRF y throttles | test_invalid_login_and_inactive_account_have_same_error; test_login_cookie_and_me |
| Identidad propia | Los tres roles autenticados | Usuario del access, nunca parámetro arbitrario; datos actuales de empresa | test_me_observes_current_assignment_not_token_claim; test_me_rejects_invalid_access |
| Refresh | Poseedor de cookie válida | CSRF, cuenta activa, consumo único y límite IP | test_refresh_rotation_replay_and_logout; test_concurrent_refresh_only_one_consumes_cookie |
| Cierre de sesión | Público con CSRF | Revoca únicamente refresh presentado; idempotente | test_refresh_rotation_replay_and_logout |
| Crear superadmin | Procedimiento local administrativo | Rol/flags coherentes, sin empresa, sin secreto fijo | test_superuser_manager_and_admin_policy; test_superuser_rejects_inconsistent_flags |
| Entrar al Admin | SUPERADMIN activo | is_staff e is_superuser verdaderos; staff aislado no basta | test_superadmin_can_open_admin_without_default_user |
| Crear empresas/sucursales/productos de configuración | SUPERADMIN en Admin | Validación de modelos, FK protegidas; sin CRUD REST de esos recursos | test_cross_company_references_and_tenant_changes_rejected; test_database_quantity_constraint_and_protected_references |
| Crear/asignar cuentas y roles | SUPERADMIN en Admin | COMPANY_ADMIN necesita empresa; flags consistentes; sin endpoint público de asignación | test_admin_creation_and_assignment_forms; test_database_rejects_privilege_escalation_bypassing_model_clean |
| Recursos privados futuros: acceso base | SUPERADMIN global o usuario de empresa activa | Sin empresa deniega; empresa inactiva deniega; objeto ajeno deniega | test_private_permission_uses_current_company_and_not_staff; test_unassigned_user_denied_on_private_policy_in_test_only_view |
| Categorías: leer | Tres roles asignados; superadmin global | Solo empresa propia para admin/operador; sin empresa deniega | test_collections_require_login_and_assigned_company; test_other_company_detail_is_404 |
| Categorías: crear/editar/borrar | SUPERADMIN y COMPANY_ADMIN | Global explícito al crear / empresa propia; sin referencias para borrar | test_category_crud_admin_and_superadmin; test_operator_cannot_administer_categories; test_category_uniqueness_scope_and_protected_delete |
| Cajas: leer/crear/editar | SUPERADMIN, COMPANY_ADMIN, OPERATOR asignado | Empresa activa, pertenencia de FK, estados y creador impuesto | test_box_create_read_put_patch_and_server_identifiers; test_foreign_or_missing_box_reference_same_safe_error; test_box_initial_state_transitions_and_terminal_immutability |
| Cajas: borrar | SUPERADMIN y COMPANY_ADMIN | Solo REGISTERED y empresa propia salvo superadmin | test_registered_box_delete_allowed_for_admin_roles; test_box_delete_permissions_and_terminal_state |
| Filtros y búsqueda | Los mismos roles de lectura | No amplían scope; campos/UUID/duplicados validados | test_lookup_by_internal_id_qr_and_related_filters_remains_scoped; test_company_filter_never_expands_scope |
| Campos protegidos | Ningún cliente puede editarlos | Company solo POST superadmin; created_by/IDs siempre servidor | test_box_rejects_mass_assignment_even_on_own_resource; test_company_readonly_for_admin_even_when_equal_and_for_super_update |
| Inventario/recepciones/reportes | Pendiente F6 | Empresa/sucursal y rol autorizados | No implementado |

La vista de prueba de F2 sigue sin publicarse. F3 ya aplica permisos y filtros de empresa a endpoints reales, con pruebas de colección/detalle/cuerpo/filtros y acceso sin asignación. No depende de ocultar botones. Usuario reasignado pierde acceso al ámbito anterior con su token existente; el creador histórico de sus cajas se conserva.

Un COMPANY_ADMIN no puede entrar al Admin global, incluso con is_staff=true; su administración web específica se implementará posteriormente. En esta fase la asignación se realiza por superadmin, desde `/admin/`, mediante formularios validados y credenciales introducidas de forma segura.

CHECKLIST HUMANO: revisar esta matriz al cerrar F3 y autorizar F4 por separado. No es necesario asignar empresa a las cuentas técnicas inactivas de F2.
