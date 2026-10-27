# Roles y permisos — Fase 2

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
| Crear empresas/sucursales/categorías/productos/cajas de configuración | SUPERADMIN en Admin | Validación de modelos, FK protegidas, sin interfaz REST aún | test_cross_company_references_and_tenant_changes_rejected; test_database_quantity_constraint_and_protected_references |
| Crear/asignar cuentas y roles | SUPERADMIN en Admin | COMPANY_ADMIN necesita empresa; flags consistentes; sin endpoint público de asignación | test_admin_creation_and_assignment_forms; test_database_rejects_privilege_escalation_bypassing_model_clean |
| Recursos privados futuros: acceso base | SUPERADMIN global o usuario de empresa activa | Sin empresa deniega; empresa inactiva deniega; objeto ajeno deniega | test_private_permission_uses_current_company_and_not_staff; test_unassigned_user_denied_on_private_policy_in_test_only_view |
| CRUD REST categorías/cajas | Pendiente F3 | Se conserva política propuesta en ARQUITECTURA; no hay rutas implementadas | Pendiente, no declarar cobertura de endpoints inexistentes |
| Inventario/recepciones/reportes | Pendiente F6 | Empresa/sucursal y rol autorizados | No implementado |

La vista usada para probar 403 por falta de empresa existe únicamente dentro de la suite y no está publicada. HasCompanyAccess incluye permiso de objeto, pero las listas también requerirán filtrado por empresa en F3; ocultar botones no será suficiente.

Un COMPANY_ADMIN no puede entrar al Admin global, incluso con is_staff=true; su administración web específica se implementará posteriormente. En esta fase la asignación se realiza por superadmin, desde `/admin/`, mediante formularios validados y credenciales introducidas de forma segura.

CHECKLIST HUMANO: revisar matriz antes de F3 y autorizar esa fase por separado. No es necesario asignar una empresa a la cuenta técnica de verificación.
