import { t, resultCount } from '../i18n/index.js'
import { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth.jsx'
import { useTenant } from '../components/AppShell.jsx'
import {
  Button,
  ConfirmModal,
  DataTable,
  EmptyState,
  ErrorState,
  FilterBar,
  FormField,
  Icon,
  LoadingState,
  Modal,
  PageIntro,
  SearchBar,
  SelectField,
  StatusBadge,
  Toast,
} from '../components/ui.jsx'
import { useDebounced, useRemote } from '../hooks/useRemote.js'
import { api } from '../services/api.js'

function CategoryForm({ record, onClose, onSaved }) {
  const tenant = useTenant(),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(null)
  async function save(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    const form = new FormData(event.currentTarget)
    const data = {
      name: form.get('name'),
      description: form.get('description'),
      is_fragile: form.get('is_fragile') === 'on',
      is_perishable: form.get('is_perishable') === 'on',
    }
    if (tenant.global && !record) data.company = form.get('company')
    try {
      await api(`/categories/${record ? `${record.id}/` : ''}`, {
        method: record ? 'PATCH' : 'POST',
        data,
      })
      onSaved(record ? t("category_updated") : t("category_created"))
    } catch (error) {
      setError(error)
    } finally {
      setBusy(false)
    }
  }
  return (
    <Modal title={record ? t("edit_category") : t("create_category")} onClose={onClose} busy={busy}>
      <form onSubmit={save}>
        <div className="modal-body">
          {error && <ErrorState error={error} />}
          {tenant.global && !record ? (
            <SelectField
              label={t("company")}
              name="company"
              options={tenant.refs.data?.companies || []}
              defaultValue={tenant.selected}
              required
            />
          ) : (
            <p className="form-context">{record?.company_name || tenant.companyName}</p>
          )}
          <FormField
            label={t("category_name")}
            name="name"
            maxLength={120}
            defaultValue={record?.name || ''}
            required
          />
          <FormField label={t("description")}>
            {(id) => (
              <textarea
                id={id}
                name="description"
                rows="3"
                defaultValue={record?.description || ''}
              />
            )}
          </FormField>
          <fieldset className="condition-options">
            <legend>{t("goods_conditions")}</legend>
            <label>
              <input type="checkbox" name="is_fragile" defaultChecked={record?.is_fragile} />
              <span>{t("fragile")}<small>{t("requires_careful_handling")}</small>
              </span>
            </label>
            <label>
              <input type="checkbox" name="is_perishable" defaultChecked={record?.is_perishable} />
              <span>{t("perishable")}<small>{t("its_conditions_change_over_time")}</small>
              </span>
            </label>
          </fieldset>
        </div>
        <footer>
          <Button variant="secondary" type="button" onClick={onClose} disabled={busy}>{t("cancel")}</Button>
          <Button variant="dark" type="submit" busy={busy}>{t("save_category")}</Button>
        </footer>
      </form>
    </Modal>
  )
}
export function BoxForm({ record, onClose, onSaved }) {
  const tenant = useTenant(),
    [company, setCompany] = useState(record?.company || tenant.selected || '')
  const [product, setProduct] = useState(record?.product || ''),
    [branch, setBranch] = useState(record?.branch || '')
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(null)
  const refs = useRemote('/references/', { company }, !!company)
  async function save(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    const form = new FormData(event.currentTarget)
    const data = {
      product,
      branch,
      quantity: Number(form.get('quantity')),
      weight_kg: form.get('weight_kg') || null,
      priority: form.get('priority'),
    }
    if (tenant.global && !record) data.company = company
    try {
      await api(`/boxes/${record ? `${record.id}/` : ''}`, {
        method: record ? 'PATCH' : 'POST',
        data,
      })
      onSaved(record ? t("box_updated") : t("box_registered_with_its_own_identification"))
    } catch (error) {
      setError(error)
    } finally {
      setBusy(false)
    }
  }
  const unavailable = !refs.data?.products.length || !refs.data?.branches.length
  return (
    <Modal title={record ? t("edit_box") : t("register_a_box")} onClose={onClose} busy={busy}>
      <form onSubmit={save}>
        <div className="modal-body">
          {error && <ErrorState error={error} />}
          {tenant.global && !record ? (
            <SelectField
              label={t("company")}
              value={company}
              onChange={(e) => {
                setCompany(e.target.value)
                setProduct('')
                setBranch('')
              }}
              options={tenant.refs.data?.companies || []}
              required
            />
          ) : (
            <p className="form-context">{record?.company_name || tenant.companyName}</p>
          )}
          {!company ? (
            <p className="inline-note">{t("select_a_company_to_view_its_products_and")}</p>
          ) : refs.loading ? (
            <LoadingState label={t("loading_authorized_references")} />
          ) : refs.error ? (
            <ErrorState error={refs.error} onRetry={refs.reload} />
          ) : (
            <>
              {unavailable && (
                <p className="inline-note">{t("active_products_or_branches_are_missing_a_superadmin")}</p>
              )}
              <SelectField
                label={t("product")}
                options={(refs.data?.products || []).map((p) => ({
                  id: p.id,
                  name: `${p.sku} · ${p.name} / ${p.category_name}`,
                }))}
                value={product}
                onChange={(e) => setProduct(e.target.value)}
                required
              />
              <SelectField
                label={t("branch")}
                options={refs.data?.branches || []}
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                required
              />
              <div className="form-grid">
                <FormField
                  label={t("quantity")}
                  name="quantity"
                  type="number"
                  min="1"
                  max="2147483647"
                  step="1"
                  defaultValue={record?.quantity || 1}
                  required
                />
                <FormField
                  label={t("weight_kg_optional")}
                  name="weight_kg"
                  type="number"
                  min="0.001"
                  max="999999999.999"
                  step="0.001"
                  defaultValue={record?.weight_kg || ''}
                />
              </div>
              <SelectField
                label={t("priority")}
                name="priority"
                options={[
                  { id: 'LOW', name: t("low") },
                  { id: 'NORMAL', name: t("normal") },
                  { id: 'HIGH', name: t("high") },
                ]}
                defaultValue={record?.priority || 'NORMAL'}
                required
              />
              <p className="inline-note">{t("the_server_assigns_the_internal_identifier_qr_code")}{' '}
                {record
                  ? t("the_company_and_creator_are_preserved")
                  : t("the_box_is_created_with_registered_status")}
              </p>
            </>
          )}
        </div>
        <footer>
          <Button variant="secondary" type="button" onClick={onClose} disabled={busy}>{t("cancel")}</Button>
          <Button
            variant="dark"
            type="submit"
            busy={busy}
            disabled={!company || refs.loading || !!refs.error || unavailable}
          >{t("save_box")}</Button>
        </footer>
      </form>
    </Modal>
  )
}
export default function Resources({ kind }) {
  const boxes = kind === 'boxes',
    auth = useAuth(),
    tenant = useTenant()
  const [search, setSearch] = useState(''),
    [mode, setMode] = useState('search'),
    [status, setStatus] = useState(''),
    [priority, setPriority] = useState(''),
    [fragile, setFragile] = useState(''),
    [perishable, setPerishable] = useState('')
  const [editor, setEditor] = useState(null),
    [remove, setRemove] = useState(null),
    [removeBusy, setRemoveBusy] = useState(false),
    [removeError, setRemoveError] = useState(null),
    [toast, setToast] = useState('')
  const closeToast = useCallback(() => setToast(''), [])
  const debounced = useDebounced(search.trim())
  const validSearch =
    !boxes ||
    !debounced ||
    mode === 'search' ||
    (mode === 'internal_id'
      ? /^CJ-[0-9a-f]{32}$/i.test(debounced)
      : /^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(debounced))
  const resource = useRemote(
    `/${kind}/`,
    {
      company: tenant.company,
      ...(boxes
        ? { [mode]: debounced, status, priority }
        : { search: debounced, is_fragile: fragile, is_perishable: perishable }),
    },
    validSearch,
  )
  const canManage = auth.user.role !== 'OPERATOR',
    canCreate = boxes || canManage
  function saved(message) {
    setEditor(null)
    setToast(message)
    resource.reload()
    tenant.refs.reload()
  }
  async function doRemove() {
    setRemoveBusy(true)
    try {
      await api(`/${kind}/${remove.id}/`, { method: 'DELETE' })
      setRemove(null)
      setToast(boxes ? t("box_deleted") : t("category_deleted"))
      resource.reload()
    } catch (error) {
      setRemoveError(error)
    } finally {
      setRemoveBusy(false)
    }
  }
  function clear() {
    setSearch('')
    setStatus('')
    setPriority('')
    setFragile('')
    setPerishable('')
  }
  const rows = resource.data || []
  const columns = boxes
    ? [
        {
          key: 'internal_id',
          title: t("identification"),
          render: (r) => (
            <>
              <Link className="mono id-link" to={`/app/cajas/${r.id}`}>
                {r.internal_id}
              </Link>
              <span className="cell-secondary">{t("independent_qr_view_details")}</span>
            </>
          ),
        },
        {
          key: 'product_name',
          title: t("product"),
          render: (r) => (
            <>
              <strong>{r.product_name}</strong>
              <span className="cell-secondary">{r.category_name}</span>
              {tenant.global && <span className="cell-secondary">{r.company_name}</span>}
            </>
          ),
        },
        {
          key: 'quantity',
          title: t("quantity"),
          render: (r) => <span className="mono">{r.quantity}</span>,
        },
        { key: 'branch_name', title: t("branch") },
        { key: 'priority', title: t("priority"), render: (r) => <StatusBadge value={r.priority} /> },
        { key: 'status', title: t("status"), render: (r) => <StatusBadge value={r.status} /> },
        {
          key: 'actions',
          title: t("actions"),
          render: (r) => (
            <div className="row-actions">
              <Link
                className="button button-text"
                to={`/app/cajas/${r.id}`}
                aria-label={t('view_box_label', { identifier: r.internal_id })}
              >{t("view")}{' '}<Icon name="arrow" />
              </Link>
              {r.status === 'REGISTERED' && (
                <button
                  className="icon-button"
                  aria-label={t('edit_box_label', { identifier: r.internal_id })}
                  onClick={() => setEditor(r)}
                >
                  <Icon name="edit" />
                </button>
              )}
            </div>
          ),
        },
      ]
    : [
        {
          key: 'name',
          title: t("category"),
          render: (r) => (
            <>
              <strong>{r.name}</strong>
              {tenant.global && <span className="cell-secondary">{r.company_name}</span>}
            </>
          ),
        },
        {
          key: 'description',
          title: t("description"),
          render: (r) => r.description || <span className="muted">{t("no_description")}</span>,
        },
        {
          key: 'conditions',
          title: t("conditions"),
          render: (r) => (
            <div className="badge-group">
              {r.is_fragile && <span className="badge badge-fragile">{t("fragile")}</span>}
              {r.is_perishable && <span className="badge badge-perishable">{t("perishable")}</span>}
              {!r.is_fragile && !r.is_perishable && <span className="muted">{t("standard")}</span>}
            </div>
          ),
        },
        ...(canManage
          ? [
              {
                key: 'actions',
                title: t("actions"),
                render: (r) => (
                  <div className="row-actions">
                    <button
                      className="button button-text"
                      onClick={() => setEditor(r)}
                      aria-label={t('edit_category_label', { name: r.name })}
                    >
                      <Icon name="edit" />{t("edit")}</button>
                    <button
                      className="button button-text danger-text"
                      onClick={() => {
                        setRemoveError(null)
                        setRemove(r)
                      }}
                      aria-label={t('delete_category_label', { name: r.name })}
                    >{t("delete")}</button>
                  </div>
                ),
              },
            ]
          : []),
      ]
  return (
    <>
      <PageIntro
        eyebrow={
          boxes ? t("registration_identification_lookup") : t("catalog_goods_conditions")
        }
        title={boxes ? t("every_box_has_an_identity") : t("classify_to_care")}
        action={
          canCreate && (
            <Button
              variant="dark"
              onClick={() => setEditor('new')}
              disabled={tenant.refs.loading || !!tenant.refs.error}
            >
              <Icon name="plus" />
              {boxes ? t("register_box") : t("create_category")}
            </Button>
          )
        }
      >
        {boxes
          ? t("view_and_manage_goods_records_within_your_authorized")
          : t("organize_categories_and_identify_the_conditions_each_product")}
      </PageIntro>
      {tenant.refs.error && <ErrorState error={tenant.refs.error} onRetry={tenant.refs.reload} />}
      <section className="workspace-section">
        <FilterBar onClear={clear}>
          <SearchBar
            value={search}
            onChange={setSearch}
            label={boxes ? t("search_boxes") : t("search_categories")}
            placeholder={
              boxes
                ? mode === 'search'
                  ? t("product_sku_or_identifier")
                  : mode === 'internal_id'
                    ? t("cj_followed_by_32_characters")
                    : t("qr_content_uuid")
                : t("name_or_description")
            }
          />
          {boxes ? (
            <>
              <SelectField
                label={t("search_by")}
                options={[
                  { id: 'search', name: t("general_search") },
                  { id: 'internal_id', name: t("exact_internal_id") },
                  { id: 'qr_code', name: t("exact_qr") },
                ]}
                value={mode}
                onChange={(e) => {
                  setMode(e.target.value || 'search')
                  setSearch('')
                }}
              />
              <SelectField
                label={t("status")}
                options={[
                  { id: 'REGISTERED', name: t("registered") },
                  { id: 'RECEIVED', name: t("received") },
                  { id: 'REJECTED', name: t("rejected") },
                ]}
                placeholder={t("all")}
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              />
              <SelectField
                label={t("priority")}
                options={[
                  { id: 'HIGH', name: t("high") },
                  { id: 'NORMAL', name: t("normal") },
                  { id: 'LOW', name: t("low") },
                ]}
                placeholder={t("all")}
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              />
            </>
          ) : (
            <>
              <SelectField
                label={t("fragility")}
                options={[
                  { id: 'true', name: t("fragile") },
                  { id: 'false', name: t("not_fragile") },
                ]}
                placeholder={t("all")}
                value={fragile}
                onChange={(e) => setFragile(e.target.value)}
              />
              <SelectField
                label={t("perishability")}
                options={[
                  { id: 'true', name: t("perishable") },
                  { id: 'false', name: t("not_perishable") },
                ]}
                placeholder={t("all")}
                value={perishable}
                onChange={(e) => setPerishable(e.target.value)}
              />
            </>
          )}
        </FilterBar>
        <div className="results-caption" aria-live="polite">
          <span>
            {resource.loading
              ? t("loading")
              : resultCount(rows.length, boxes)}
          </span>
          <span>{tenant.companyName}</span>
        </div>
        {!validSearch ? (
          <EmptyState title={t("enter_the_complete_identifier")}>{t("exact_search_requires_the_complete_code_you_can")}</EmptyState>
        ) : resource.loading ? (
          <LoadingState />
        ) : resource.error ? (
          <ErrorState error={resource.error} onRetry={resource.reload} />
        ) : rows.length ? (
          <DataTable
            caption={boxes ? t("authorized_boxes") : t("authorized_categories")}
            columns={columns}
            rows={rows}
          />
        ) : (
          <EmptyState
            title={
              search || status || priority || fragile || perishable
                ? t("no_matches_for_these_filters")
                : boxes
                  ? t("your_first_box_starts_here")
                  : t("no_categories_yet")
            }
          >{t("try_other_filters_or_register_a_resource_if")}</EmptyState>
        )}
      </section>
      <p className="scope-note">{t("the_api_enforces_permissions")}{' '}
        {boxes
          ? t("final_statuses_prevent_changes_and_deletion_within_this")
          : canManage
            ? t("categories_referenced_by_products_cannot_be_deleted")
            : t("your_operator_role_allows_viewing_categories_but_not")}
      </p>
      {editor &&
        (boxes ? (
          <BoxForm
            record={editor === 'new' ? null : editor}
            onClose={() => setEditor(null)}
            onSaved={saved}
          />
        ) : (
          <CategoryForm
            record={editor === 'new' ? null : editor}
            onClose={() => setEditor(null)}
            onSaved={saved}
          />
        ))}
      {remove && (
        <ConfirmModal
          title={t('delete_category')}
          busy={removeBusy}
          error={removeError}
          onClose={() => setRemove(null)}
          onConfirm={doRemove}
        >{t("delete_2")}{remove.name}{t("the_operation_will_be_rejected_if_references_exist")}</ConfirmModal>
      )}
      {toast && <Toast message={toast} onClose={closeToast} />}
    </>
  )
}
