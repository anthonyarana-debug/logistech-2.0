import { useCallback, useState } from 'react'
import { useAuth } from '../auth.jsx'
import { useTenant, roleNames } from '../components/AppShell.jsx'
import {
  Button, ConfirmModal, DataTable, EmptyState, ErrorState, FilterBar, FormField,
  LoadingState, Modal, PageIntro, PasswordField, SearchBar, SelectField, StatusBadge, Toast,
} from '../components/ui.jsx'
import { useDebounced, useRemote } from '../hooks/useRemote.js'
import { t, formatNumber } from '../i18n/index.js'
import { api } from '../services/api.js'
import { canAdminister, canEditUser } from '../services/operations.js'
import { NotFound } from './Special.jsx'

const createKeys = { companies: 'ops_create_company', branches: 'ops_create_branch', products: 'ops_create_product', users: 'ops_create_user' }

function RecordForm({ kind, record, onClose, onSaved }) {
  const tenant = useTenant()
  const users = kind === 'users', products = kind === 'products', companies = kind === 'companies'
  const [company, setCompany] = useState(record?.company || tenant.selected || '')
  const [role, setRole] = useState(record?.role || 'OPERATOR')
  const [branch, setBranch] = useState(record?.branch || '')
  const [category, setCategory] = useState(record?.category || '')
  const [busy, setBusy] = useState(false), [error, setError] = useState(null)
  const refs = useRemote('/references/', { company }, !!company && products)
  const userBranches = useRemote('/branches/', { company, status: 'ACTIVE' }, !!company && users)
  const companyOptions = [...(tenant.refs.data?.companies || [])]
  if (record?.company && !companyOptions.some(c => c.id === record.company))
    companyOptions.push({ id: record.company, name: record.company_name })
  const branchOptions = [...(userBranches.data || [])]
  if (record?.branch && company === record.company && !branchOptions.some(b => b.id === record.branch))
    branchOptions.push({ id: record.branch, name: record.branch_name })
  async function save(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    const form = new FormData(event.currentTarget)
    const data = users ? {
      email: form.get('email'), first_name: form.get('first_name'), last_name: form.get('last_name'),
      branch: branch || null, is_active: form.get('is_active') === 'true',
    } : { name: form.get('name'), status: form.get('status') }
    if (users) {
      if (form.get('password')) data.password = form.get('password')
      if (tenant.global) { data.company = company || null; data.role = role }
    } else {
      if (kind === 'branches') data.address = form.get('address')
      if (products) { data.sku = form.get('sku'); data.category = category; data.description = form.get('description') }
      if (!companies && tenant.global && !record) data.company = company
    }
    try {
      await api(`/${kind}/${record ? `${record.id}/` : ''}`, { method: record ? 'PATCH' : 'POST', data })
      onSaved()
    } catch (error) { setError(error) } finally { setBusy(false) }
  }
  const companyPicker = !companies && tenant.global && (users || !record)
  return (
    <Modal title={record ? t('ops_edit_record') : t(createKeys[kind])} onClose={onClose} busy={busy}>
      <form onSubmit={save}>
        <div className="modal-body">
          {error && <ErrorState error={error} />}
          {companyPicker && <SelectField label={t('company')} options={companyOptions}
            value={company} onChange={e => { setCompany(e.target.value); setBranch(''); setCategory('') }}
            required={!users || role === 'COMPANY_ADMIN'} placeholder={users ? t('ops_unassigned') : t('select')} />}
          {users ? <>
            <FormField label={t('email_address')} name="email" type="email" maxLength={254} defaultValue={record?.email || ''} required />
            <div className="form-grid">
              <FormField label={t('first_name')} name="first_name" maxLength={150} defaultValue={record?.first_name || ''} />
              <FormField label={t('last_name')} name="last_name" maxLength={150} defaultValue={record?.last_name || ''} />
            </div>
            {!record && <PasswordField name="password" minLength={12} maxLength={128} required
              autoComplete="new-password" hint={t('ops_password_hint')} />}
            {tenant.global && <SelectField label={t('ops_role')} options={['OPERATOR', 'COMPANY_ADMIN'].map(id => ({ id, name: roleNames[id] }))}
              value={role} onChange={e => setRole(e.target.value)} required />}
            {userBranches.loading ? <LoadingState /> : userBranches.error ? <ErrorState error={userBranches.error} onRetry={userBranches.reload} /> :
              <SelectField label={t('ops_assigned_branch')} value={branch} onChange={e => setBranch(e.target.value)}
                options={branchOptions} placeholder={t('ops_no_branch')} disabled={!company} />}
            <SelectField label={t('ops_account_status')} name="is_active"
              defaultValue={record?.is_active === false ? 'false' : 'true'} required
              options={[{ id: 'true', name: t('ops_active') }, { id: 'false', name: t('ops_inactive') }]} />
            <p className="inline-note">{t('ops_user_policy')}</p>
          </> : <>
            <FormField label={t('ops_name')} name="name" maxLength={kind === 'branches' ? 120 : 160} defaultValue={record?.name || ''} required />
            {kind === 'branches' && <FormField label={t('ops_address')} name="address" maxLength={240} defaultValue={record?.address || ''} />}
            {products && <>
              <FormField label={t('ops_sku')} name="sku" maxLength={64} defaultValue={record?.sku || ''} required />
              {refs.loading ? <LoadingState /> : refs.error ? <ErrorState error={refs.error} onRetry={refs.reload} /> :
                <SelectField label={t('category')} options={refs.data?.categories || []} value={category}
                  onChange={e => setCategory(e.target.value)} required disabled={!company} />}
              <FormField label={t('description')} name="description" maxLength={4000} defaultValue={record?.description || ''} />
            </>}
            <SelectField label={t('status')} name="status" defaultValue={record?.status || 'ACTIVE'} required
              options={[{ id: 'ACTIVE', name: t('ops_active') }, { id: 'INACTIVE', name: t('ops_inactive') }]} />
          </>}
        </div>
        <footer>
          <Button variant="secondary" type="button" onClick={onClose} disabled={busy}>{t('cancel')}</Button>
          <Button variant="dark" type="submit" busy={busy} disabled={products ? (refs.loading || !!refs.error) : users && (userBranches.loading || !!userBranches.error)}>{t('ops_save_changes')}</Button>
        </footer>
      </form>
    </Modal>
  )
}

function AdministrationBody({ kind }) {
  const auth = useAuth(), tenant = useTenant()
  const users = kind === 'users', companies = kind === 'companies'
  const [search, setSearch] = useState(''), [status, setStatus] = useState(''), [role, setRole] = useState('')
  const [editor, setEditor] = useState(null), [remove, setRemove] = useState(null)
  const [busy, setBusy] = useState(false), [removeError, setRemoveError] = useState(null), [toast, setToast] = useState('')
  const closeToast = useCallback(() => setToast(''), [])
  const resource = useRemote(`/${kind}/`, {
    ...(!companies ? { company: tenant.company } : {}), search: useDebounced(search.trim()),
    ...(users ? { is_active: status, role } : { status }),
  })
  const manage = canAdminister(auth.user, kind)
  const editable = record => users ? canEditUser(auth.user, record) : manage
  function saved() {
    setEditor(null); setToast(t('ops_saved')); resource.reload(); tenant.refs.reload()
  }
  async function destroy() {
    setBusy(true); setRemoveError(null)
    try {
      await api(`/${kind}/${remove.id}/`, { method: 'DELETE' })
      setRemove(null); setToast(t('ops_deleted')); resource.reload(); tenant.refs.reload()
    } catch (error) { setRemoveError(error) } finally { setBusy(false) }
  }
  const columns = [
    { key: users ? 'email' : 'name', title: users ? t('email_address') : t('ops_name') },
    ...(companies ? [] : [{ key: 'company_name', title: t('company'), render: r => r.company_name || t('ops_unassigned') }]),
    ...(kind === 'branches' ? [{ key: 'address', title: t('ops_address') }] : []),
    ...(kind === 'products' ? [{ key: 'sku', title: t('ops_sku') }, { key: 'category_name', title: t('category') }] : []),
    ...(users ? [{ key: 'role', title: t('ops_role'), render: r => roleNames[r.role] },
      { key: 'branch_name', title: t('ops_assigned_branch'), render: r => r.branch_name || t('ops_no_branch') }] : []),
    { key: 'status', title: t('status'), render: r => users ? t(r.is_active ? 'ops_active' : 'ops_inactive') : <StatusBadge value={r.status} /> },
    ...(manage ? [{ key: 'actions', title: t('actions'), render: r => editable(r) && <div className="row-actions">
      <Button variant="text" onClick={() => setEditor(r)} aria-label={t('ops_edit_label', { name: r.name || r.email })}>{t('edit')}</Button>
      {!users && <Button variant="text" className="danger-text" onClick={() => { setRemove(r); setRemoveError(null) }}
        aria-label={t('ops_delete_label', { name: r.name })}>{t('ops_delete')}</Button>}
    </div> }] : []),
  ]
  return <>
    <PageIntro eyebrow={t('ops_administration')} title={t(`ops_${kind}`)}
      action={manage && <Button variant="dark" onClick={() => setEditor('new')}>{t(createKeys[kind])}</Button>}>
      {t(users ? 'ops_users_description' : 'ops_resource_description')}
    </PageIntro>
    <section className="workspace-section">
      <FilterBar onClear={() => { setSearch(''); setStatus(''); setRole('') }}>
        <SearchBar value={search} onChange={setSearch} />
        <SelectField label={t('status')} value={status} onChange={e => setStatus(e.target.value)} placeholder={t('ops_all_statuses')}
          options={(users ? ['true', 'false'] : ['ACTIVE', 'INACTIVE']).map((id, i) => ({ id, name: t(i ? 'ops_inactive' : 'ops_active') }))} />
        {users && <SelectField label={t('ops_role')} value={role} onChange={e => setRole(e.target.value)}
          placeholder={t('ops_all_roles')} options={Object.entries(roleNames).map(([id, name]) => ({ id, name }))} />}
      </FilterBar>
      <p className="results-caption" aria-live="polite">{resource.loading ? t('loading') : t('ops_records', { count: formatNumber(resource.data?.length || 0) })}</p>
      {resource.loading ? <LoadingState /> : resource.error ? <ErrorState error={resource.error} onRetry={resource.reload} /> :
        resource.data?.length ? <DataTable caption={t(`ops_${kind}`)} rows={resource.data} columns={columns} /> :
          <EmptyState title={t('no_matches_for_these_filters')}>{t('ops_empty')}</EmptyState>}
    </section>
    {editor && <RecordForm kind={kind} record={editor === 'new' ? null : editor} onClose={() => setEditor(null)} onSaved={saved} />}
    {remove && <ConfirmModal title={t('ops_confirm_delete')} busy={busy} error={removeError}
      onClose={() => setRemove(null)} onConfirm={destroy}>{t('ops_delete_note', { name: remove.name })}</ConfirmModal>}
    {toast && <Toast message={toast} onClose={closeToast} />}
  </>
}

export default function Administration({ kind }) {
  const { user } = useAuth()
  if ((kind === 'companies' || kind === 'users') && !canAdminister(user, kind)) return <NotFound forbidden />
  return <AdministrationBody kind={kind} />
}
