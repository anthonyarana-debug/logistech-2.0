"""Centralized English messages at presentation boundaries; never translate stored data."""

MESSAGES = {
    "demo_help": "Create two DEMO companies and random credentials in a new private file.",
    "demo_namespace": "Namespace: 3–32 lowercase letters, numbers or hyphens.",
    "demo_exists": (
        "The namespace or file already exists. Use new values; existing credentials are preserved."
    ),
    "demo_created": "DEMO data created. Credentials are only available in {target}.",
    "email_is_required": (
        "Email is required."
    ),
    "the_superadmin_requires_consistent_flags_and_global_scope": (
        "The superadmin requires consistent flags and global scope."
    ),
    "an_assigned_active_company_is_required_to_access_this_resource": (
        "An assigned active company is required to access this resource."
    ),
    "invalid_credentials_or_unavailable_account": (
        "Invalid credentials or unavailable account."
    ),
    "a_json_object_is_required": (
        "A JSON object is required."
    ),
    "the_request_contains_fields_that_are_not_allowed": (
        "The request contains fields that are not allowed."
    ),
    "registration_could_not_be_completed_with_the_supplied_data": (
        "Registration could not be completed with the supplied data."
    ),
    "the_session_is_unavailable": (
        "The session is unavailable."
    ),
    "a_unique_identifier_could_not_be_generated_please_try_again": (
        "A unique identifier could not be generated. Please try again."
    ),
    "reference_unavailable": (
        "Reference unavailable."
    ),
    "reference_unavailable_for_this_company": (
        "Reference unavailable for this company."
    ),
    "a_new_box_must_have_registered_status": (
        "A new box must have registered status."
    ),
    "a_received_or_rejected_box_cannot_be_modified_in_this_crud": (
        "A received or rejected box cannot be modified in this CRUD."
    ),
    "only_registered_boxes_without_reception_or_rejection_can_be_deleted": (
        "Only registered boxes without reception or rejection can be deleted."
    ),
    "a_reference_is_no_longer_available": (
        "A reference is no longer available."
    ),
    "references_must_be_active_and_belong_to_the_company": (
        "References must be active and belong to the company."
    ),
    "invalid_internal_identifier": (
        "Invalid internal identifier."
    ),
    "references_must_belong_to_the_company": (
        "References must belong to the company."
    ),
    "a_category_with_this_name_already_exists_in_the_company": (
        "A category with this name already exists in the company."
    ),
    "the_category_conflicts_with_an_existing_record": (
        "The category conflicts with an existing record."
    ),
    "use_true_or_false": (
        "Use true or false."
    ),
    "the_operation_conflicts_with_the_resource_status_or_references": (
        "The operation conflicts with the resource status or references."
    ),
    "you_do_not_have_permission_to_perform_this_operation": (
        "You do not have permission to perform this operation."
    ),
    "the_account_is_unavailable": (
        "The account is unavailable."
    ),
    "the_company_is_unavailable": (
        "The company is unavailable."
    ),
    "the_company_must_be_active_to_modify_resources": (
        "The company must be active to modify resources."
    ),
    "filters_are_only_accepted_on_the_collection": (
        "Filters are only accepted on the collection."
    ),
    "unknown_or_repeated_filter": (
        "Unknown or repeated filter."
    ),
    "you_do_not_have_permission_to_access_that_scope": (
        "You do not have permission to access that scope."
    ),
    "the_data_does_not_meet_the_resource_rules": (
        "The data does not meet the resource rules."
    ),
    "explicitly_select_an_active_company": (
        "Explicitly select an active company."
    ),
    "use_between_1_and_100_characters": (
        "Use between 1 and 100 characters."
    ),
    "a_valid_uuid_is_required": (
        "A valid UUID is required."
    ),
    "filter_value_not_allowed": (
        "Filter value not allowed."
    ),
    "do_not_enable_authentication_with_auth_user": (
        "Do not enable authentication with auth.User."
    ),
    "create_accounts_user_and_its_0001_initial_before_migrating_auth_admin": (
        "Create accounts.User and its 0001_initial before migrating auth/admin."
    ),
    "csrf_verification_failed": (
        "CSRF verification failed."
    ),
    "internal_service_error": (
        "Internal service error."
    ),
    "invalid_credentials_or_session": (
        "Invalid credentials or session."
    ),
    "too_many_requests_please_try_again_later": (
        "Too many requests. Please try again later."
    ),
    "company_unavailable": (
        "Company unavailable."
    ),
    "resource_not_found": (
        "Resource not found."
    ),
    "data_dependency_unavailable": (
        "Data dependency unavailable."
    ),
    "the_resource_must_belong_to_the_same_company": (
        "The resource must belong to the same company."
    ),
    "the_creator_must_belong_to_the_company": (
        "The creator must belong to the company."
    ),
    "the_original_creator_cannot_be_changed": (
        "The original creator cannot be changed."
    ),
    "the_role_and_superuser_flag_must_match": (
        "The role and superuser flag must match."
    ),
    "the_superadmin_must_be_staff_and_have_no_company": (
        "The superadmin must be staff and have no company."
    ),
    "the_administrator_must_have_an_assigned_company": (
        "The administrator must have an assigned company."
    ),
    "the_resource_company_cannot_be_changed": (
        "The resource company cannot be changed."
    ),
    "the_name_cannot_be_empty": (
        "The name cannot be empty."
    ),
    "the_category_must_belong_to_the_same_company": (
        "The category must belong to the same company."
    ),
}


def message(key):
    """Return a known English message; unknown keys are programming errors."""
    return MESSAGES[key]


LEGACY_DOMAIN_MESSAGES = {
    "El correo es obligatorio.": (
        "Email is required."
    ),
    "El superadministrador requiere flags coherentes y alcance global.": (
        "The superadmin requires consistent flags and global scope."
    ),
    "Se requiere una empresa activa asignada para acceder a este recurso.": (
        "An assigned active company is required to access this resource."
    ),
    "Credenciales inválidas o cuenta no disponible.": (
        "Invalid credentials or unavailable account."
    ),
    "Se requiere un objeto JSON.": (
        "A JSON object is required."
    ),
    "La solicitud contiene campos no permitidos.": (
        "The request contains fields that are not allowed."
    ),
    "No se pudo registrar con los datos proporcionados.": (
        "Registration could not be completed with the supplied data."
    ),
    "La sesión no está disponible.": (
        "The session is unavailable."
    ),
    "No se pudo generar un identificador único. Intenta nuevamente.": (
        "A unique identifier could not be generated. Please try again."
    ),
    "Referencia no disponible.": (
        "Reference unavailable."
    ),
    "Referencia no disponible para esta empresa.": (
        "Reference unavailable for this company."
    ),
    "Una caja nueva debe estar registrada.": (
        "A new box must have registered status."
    ),
    "Una caja recibida o rechazada no admite modificaciones en este CRUD.": (
        "A received or rejected box cannot be modified in this CRUD."
    ),
    "Solo se pueden eliminar cajas registradas sin recepción ni rechazo.": (
        "Only registered boxes without reception or rejection can be deleted."
    ),
    "Una referencia ya no está disponible.": (
        "A reference is no longer available."
    ),
    "Las referencias deben estar activas y pertenecer a la empresa.": (
        "References must be active and belong to the company."
    ),
    "Identificador interno no válido.": (
        "Invalid internal identifier."
    ),
    "Las referencias deben pertenecer a la empresa.": (
        "References must belong to the company."
    ),
    "Ya existe una categoría con ese nombre en la empresa.": (
        "A category with this name already exists in the company."
    ),
    "La categoría entra en conflicto con un registro existente.": (
        "The category conflicts with an existing record."
    ),
    "Usa true o false.": (
        "Use true or false."
    ),
    "La operación entra en conflicto con el estado o las referencias del recurso.": (
        "The operation conflicts with the resource status or references."
    ),
    "No tienes permiso para realizar esta operación.": (
        "You do not have permission to perform this operation."
    ),
    "La cuenta no está disponible.": (
        "The account is unavailable."
    ),
    "La empresa no está disponible.": (
        "The company is unavailable."
    ),
    "La empresa debe estar activa para modificar recursos.": (
        "The company must be active to modify resources."
    ),
    "Los filtros solo se admiten en la colección.": (
        "Filters are only accepted on the collection."
    ),
    "Filtro desconocido o repetido.": (
        "Unknown or repeated filter."
    ),
    "No tienes permiso para consultar ese ámbito.": (
        "You do not have permission to access that scope."
    ),
    "Los datos no cumplen las reglas del recurso.": (
        "The data does not meet the resource rules."
    ),
    "Elige explícitamente una empresa activa.": (
        "Explicitly select an active company."
    ),
    "Usa entre 1 y 100 caracteres.": (
        "Use between 1 and 100 characters."
    ),
    "Se requiere un UUID válido.": (
        "A valid UUID is required."
    ),
    "Valor de filtro no permitido.": (
        "Filter value not allowed."
    ),
    "No habilites autenticación con auth.User.": (
        "Do not enable authentication with auth.User."
    ),
    "Crea accounts.User y su 0001_initial antes de migrar auth/admin.": (
        "Create accounts.User and its 0001_initial before migrating auth/admin."
    ),
    "La verificación CSRF no fue válida.": (
        "CSRF verification failed."
    ),
    "Error interno del servicio.": (
        "Internal service error."
    ),
    "Credenciales o sesión no válidas.": (
        "Invalid credentials or session."
    ),
    "Demasiadas solicitudes. Intenta nuevamente más tarde.": (
        "Too many requests. Please try again later."
    ),
    "Empresa no disponible.": (
        "Company unavailable."
    ),
    "Recurso no encontrado.": (
        "Resource not found."
    ),
    "Dependencia de datos no disponible.": (
        "Data dependency unavailable."
    ),
    "El recurso debe pertenecer a la misma empresa.": (
        "The resource must belong to the same company."
    ),
    "El creador debe pertenecer a la empresa.": (
        "The creator must belong to the company."
    ),
    "No se permite cambiar el creador histórico.": (
        "The original creator cannot be changed."
    ),
    "El rol y el indicador de superusuario deben coincidir.": (
        "The role and superuser flag must match."
    ),
    "El superadministrador debe ser staff y no tener empresa.": (
        "The superadmin must be staff and have no company."
    ),
    "El administrador debe tener una empresa asignada.": (
        "The administrator must have an assigned company."
    ),
    "No se permite cambiar la empresa del recurso.": (
        "The resource company cannot be changed."
    ),
    "El nombre no puede estar vacío.": (
        "The name cannot be empty."
    ),
    "La categoría debe pertenecer a la misma empresa.": (
        "The category must belong to the same company."
    ),
}


def domain_message(value):
    """Translate known model validation messages without modifying model metadata."""
    return LEGACY_DOMAIN_MESSAGES.get(value, value)
