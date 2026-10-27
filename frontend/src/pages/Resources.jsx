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
      onSaved(record ? 'Categoría actualizada.' : 'Categoría creada.')
    } catch (error) {
      setError(error)
    } finally {
      setBusy(false)
    }
  }
  return (
    <Modal title={record ? 'Editar categoría' : 'Crear categoría'} onClose={onClose} busy={busy}>
      <form onSubmit={save}>
        <div className="modal-body">
          {error && <ErrorState error={error} />}
          {tenant.global && !record ? (
            <SelectField
              label="Empresa"
              name="company"
              options={tenant.refs.data?.companies || []}
              defaultValue={tenant.selected}
              required
            />
          ) : (
            <p className="form-context">{record?.company_name || tenant.companyName}</p>
          )}
          <FormField
            label="Nombre de categoría"
            name="name"
            maxLength={120}
            defaultValue={record?.name || ''}
            required
          />
          <FormField label="Descripción">
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
            <legend>Condiciones de la mercancía</legend>
            <label>
              <input type="checkbox" name="is_fragile" defaultChecked={record?.is_fragile} />
              <span>
                Frágil<small>Requiere cuidado en su manipulación.</small>
              </span>
            </label>
            <label>
              <input type="checkbox" name="is_perishable" defaultChecked={record?.is_perishable} />
              <span>
                Perecedera<small>Sus condiciones cambian con el tiempo.</small>
              </span>
            </label>
          </fieldset>
        </div>
        <footer>
          <Button variant="secondary" type="button" onClick={onClose} disabled={busy}>
            Cancelar
          </Button>
          <Button variant="dark" type="submit" busy={busy}>
            Guardar categoría
          </Button>
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
      onSaved(record ? 'Caja actualizada.' : 'Caja registrada con identificación propia.')
    } catch (error) {
      setError(error)
    } finally {
      setBusy(false)
    }
  }
  const unavailable = !refs.data?.products.length || !refs.data?.branches.length
  return (
    <Modal title={record ? 'Editar caja' : 'Registrar una caja'} onClose={onClose} busy={busy}>
      <form onSubmit={save}>
        <div className="modal-body">
          {error && <ErrorState error={error} />}
          {tenant.global && !record ? (
            <SelectField
              label="Empresa"
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
            <p className="inline-note">
              Selecciona una empresa para consultar sus productos y sucursales.
            </p>
          ) : refs.loading ? (
            <LoadingState label="Consultando referencias autorizadas…" />
          ) : refs.error ? (
            <ErrorState error={refs.error} onRetry={refs.reload} />
          ) : (
            <>
              {unavailable && (
                <p className="inline-note">
                  Faltan productos o sucursales activos. Un superadministrador debe prepararlos
                  mediante el procedimiento de configuración.
                </p>
              )}
              <SelectField
                label="Producto"
                options={(refs.data?.products || []).map((p) => ({
                  id: p.id,
                  name: `${p.sku} · ${p.name} / ${p.category_name}`,
                }))}
                value={product}
                onChange={(e) => setProduct(e.target.value)}
                required
              />
              <SelectField
                label="Sucursal"
                options={refs.data?.branches || []}
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                required
              />
              <div className="form-grid">
                <FormField
                  label="Cantidad"
                  name="quantity"
                  type="number"
                  min="1"
                  max="2147483647"
                  step="1"
                  defaultValue={record?.quantity || 1}
                  required
                />
                <FormField
                  label="Peso (kg), opcional"
                  name="weight_kg"
                  type="number"
                  min="0.001"
                  max="999999999.999"
                  step="0.001"
                  defaultValue={record?.weight_kg || ''}
                />
              </div>
              <SelectField
                label="Prioridad"
                name="priority"
                options={[
                  { id: 'LOW', name: 'Baja' },
                  { id: 'NORMAL', name: 'Normal' },
                  { id: 'HIGH', name: 'Alta' },
                ]}
                defaultValue={record?.priority || 'NORMAL'}
                required
              />
              <p className="inline-note">
                El identificador interno, el QR y el creador los asigna el servidor.{' '}
                {record
                  ? 'La empresa y el creador se conservan.'
                  : 'La caja se crea en estado registrada.'}
              </p>
            </>
          )}
        </div>
        <footer>
          <Button variant="secondary" type="button" onClick={onClose} disabled={busy}>
            Cancelar
          </Button>
          <Button
            variant="dark"
            type="submit"
            busy={busy}
            disabled={!company || refs.loading || !!refs.error || unavailable}
          >
            Guardar caja
          </Button>
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
      setToast(boxes ? 'Caja eliminada.' : 'Categoría eliminada.')
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
          title: 'Identificación',
          render: (r) => (
            <>
              <Link className="mono id-link" to={`/app/cajas/${r.id}`}>
                {r.internal_id}
              </Link>
              <span className="cell-secondary">QR independiente · ver detalle</span>
            </>
          ),
        },
        {
          key: 'product_name',
          title: 'Producto',
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
          title: 'Cantidad',
          render: (r) => <span className="mono">{r.quantity}</span>,
        },
        { key: 'branch_name', title: 'Sucursal' },
        { key: 'priority', title: 'Prioridad', render: (r) => <StatusBadge value={r.priority} /> },
        { key: 'status', title: 'Estado', render: (r) => <StatusBadge value={r.status} /> },
        {
          key: 'actions',
          title: 'Acciones',
          render: (r) => (
            <div className="row-actions">
              <Link
                className="button button-text"
                to={`/app/cajas/${r.id}`}
                aria-label={`Ver caja ${r.internal_id}`}
              >
                Ver <Icon name="arrow" />
              </Link>
              {r.status === 'REGISTERED' && (
                <button
                  className="icon-button"
                  aria-label={`Editar caja ${r.internal_id}`}
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
          title: 'Categoría',
          render: (r) => (
            <>
              <strong>{r.name}</strong>
              {tenant.global && <span className="cell-secondary">{r.company_name}</span>}
            </>
          ),
        },
        {
          key: 'description',
          title: 'Descripción',
          render: (r) => r.description || <span className="muted">Sin descripción</span>,
        },
        {
          key: 'conditions',
          title: 'Condiciones',
          render: (r) => (
            <div className="badge-group">
              {r.is_fragile && <span className="badge badge-fragile">Frágil</span>}
              {r.is_perishable && <span className="badge badge-perishable">Perecedera</span>}
              {!r.is_fragile && !r.is_perishable && <span className="muted">Estándar</span>}
            </div>
          ),
        },
        ...(canManage
          ? [
              {
                key: 'actions',
                title: 'Acciones',
                render: (r) => (
                  <div className="row-actions">
                    <button
                      className="button button-text"
                      onClick={() => setEditor(r)}
                      aria-label={`Editar categoría ${r.name}`}
                    >
                      <Icon name="edit" />
                      Editar
                    </button>
                    <button
                      className="button button-text danger-text"
                      onClick={() => {
                        setRemoveError(null)
                        setRemove(r)
                      }}
                      aria-label={`Eliminar categoría ${r.name}`}
                    >
                      Eliminar
                    </button>
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
          boxes ? 'REGISTRO / IDENTIFICACIÓN / CONSULTA' : 'CATÁLOGO / CONDICIONES DE MERCANCÍA'
        }
        title={boxes ? 'Cada caja tiene identidad.' : 'Clasificar para cuidar.'}
        action={
          canCreate && (
            <Button
              variant="dark"
              onClick={() => setEditor('new')}
              disabled={tenant.refs.loading || !!tenant.refs.error}
            >
              <Icon name="plus" />
              {boxes ? 'Registrar caja' : 'Crear categoría'}
            </Button>
          )
        }
      >
        {boxes
          ? 'Consulta y gestiona los registros de mercancía de tu ámbito autorizado.'
          : 'Organiza categorías y distingue las condiciones que requiere cada producto.'}
      </PageIntro>
      {tenant.refs.error && <ErrorState error={tenant.refs.error} onRetry={tenant.refs.reload} />}
      <section className="workspace-section">
        <FilterBar onClear={clear}>
          <SearchBar
            value={search}
            onChange={setSearch}
            label={boxes ? 'Buscar cajas' : 'Buscar categorías'}
            placeholder={
              boxes
                ? mode === 'search'
                  ? 'Producto, SKU o identificador…'
                  : mode === 'internal_id'
                    ? 'CJ- seguido de 32 caracteres'
                    : 'Contenido del QR (UUID)'
                : 'Nombre o descripción…'
            }
          />
          {boxes ? (
            <>
              <SelectField
                label="Buscar por"
                options={[
                  { id: 'search', name: 'Búsqueda general' },
                  { id: 'internal_id', name: 'ID interno exacto' },
                  { id: 'qr_code', name: 'QR exacto' },
                ]}
                value={mode}
                onChange={(e) => {
                  setMode(e.target.value || 'search')
                  setSearch('')
                }}
              />
              <SelectField
                label="Estado"
                options={[
                  { id: 'REGISTERED', name: 'Registrada' },
                  { id: 'RECEIVED', name: 'Recibida' },
                  { id: 'REJECTED', name: 'Rechazada' },
                ]}
                placeholder="Todos"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              />
              <SelectField
                label="Prioridad"
                options={[
                  { id: 'HIGH', name: 'Alta' },
                  { id: 'NORMAL', name: 'Normal' },
                  { id: 'LOW', name: 'Baja' },
                ]}
                placeholder="Todas"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              />
            </>
          ) : (
            <>
              <SelectField
                label="Fragilidad"
                options={[
                  { id: 'true', name: 'Frágil' },
                  { id: 'false', name: 'No frágil' },
                ]}
                placeholder="Todas"
                value={fragile}
                onChange={(e) => setFragile(e.target.value)}
              />
              <SelectField
                label="Perecibilidad"
                options={[
                  { id: 'true', name: 'Perecedera' },
                  { id: 'false', name: 'No perecedera' },
                ]}
                placeholder="Todas"
                value={perishable}
                onChange={(e) => setPerishable(e.target.value)}
              />
            </>
          )}
        </FilterBar>
        <div className="results-caption" aria-live="polite">
          <span>
            {resource.loading
              ? 'Consultando…'
              : `${rows.length} ${boxes ? 'cajas' : 'categorías'} en esta consulta`}
          </span>
          <span>{tenant.companyName}</span>
        </div>
        {!validSearch ? (
          <EmptyState title="Completa el identificador">
            La búsqueda exacta necesita el código completo. También puedes cambiar a búsqueda
            general.
          </EmptyState>
        ) : resource.loading ? (
          <LoadingState />
        ) : resource.error ? (
          <ErrorState error={resource.error} onRetry={resource.reload} />
        ) : rows.length ? (
          <DataTable
            caption={boxes ? 'Cajas autorizadas' : 'Categorías autorizadas'}
            columns={columns}
            rows={rows}
          />
        ) : (
          <EmptyState
            title={
              search || status || priority || fragile || perishable
                ? 'No hay coincidencias con estos filtros'
                : boxes
                  ? 'Tu primera caja empieza aquí'
                  : 'Todavía no hay categorías'
            }
          >
            Prueba otros filtros o registra un recurso si tu rol lo permite.
          </EmptyState>
        )}
      </section>
      <p className="scope-note">
        La API es la autoridad de permisos.{' '}
        {boxes
          ? 'Los estados finales no admiten cambios ni eliminación en este alcance.'
          : canManage
            ? 'Las categorías referenciadas por productos no se pueden eliminar.'
            : 'Tu rol de operador permite consultar categorías, sin administrarlas.'}
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
          title="Eliminar categoría"
          busy={removeBusy}
          error={removeError}
          onClose={() => setRemove(null)}
          onConfirm={doRemove}
        >
          Se eliminará «{remove.name}». La operación se rechazará si existen referencias. Esta
          acción no se puede deshacer.
        </ConfirmModal>
      )}
      {toast && <Toast message={toast} onClose={closeToast} />}
    </>
  )
}
