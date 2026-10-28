// Presentation policy only. Every operation is independently authorized by the API.
export function canAdminister(user, resource) {
  if (!['companies', 'branches', 'products', 'users', 'categories'].includes(resource)) return false
  if (user?.role === 'SUPERADMIN') return true
  return user?.role === 'COMPANY_ADMIN' && !!user.company?.id && resource !== 'companies'
}

export function canEditUser(actor, target) {
  if (!target || actor.id === target.id || target.role === 'SUPERADMIN') return false
  return actor.role === 'SUPERADMIN' || (
    canAdminister(actor, 'users') && target.role === 'OPERATOR' && target.company === actor.company.id
  )
}

export function dashboardKey(role) {
  return { SUPERADMIN: 'global_operations', COMPANY_ADMIN: 'company_operations' }[role] || 'operator_workspace'
}
