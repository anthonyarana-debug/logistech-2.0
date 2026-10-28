"""English administrative messages, kept outside model/API identifiers."""

TEXT = {
    "duplicate_email": "A user with this email already exists.",
    "password_required": "A password is required.",
    "company_required": "Select an active company for this role or branch assignment.",
    "branch_scope": "Select an active branch in the user's company.",
    "category_scope": "Select a category in the product's company.",
    "duplicate": "A record with this identifier already exists in the company.",
    "protected_user": "This account cannot be modified through operational administration.",
    "operator_only": "Company administrators may manage only operators in their company.",
    "root_role": "Operational administration cannot grant the Superadmin role.",
    "company_status": "The company must be active for this assignment.",
    "invalid_object": "A JSON object with writable fields is required.",
    "invalid_filters": "Unknown, repeated or invalid filter.",
    "scope_denied": "You do not have permission to access that company.",
}


def text(key):
    return TEXT[key]
