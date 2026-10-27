import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../auth.jsx'
import {
  Button,
  ConfirmModal,
  ErrorState,
  Icon,
  LoadingState,
  Modal,
  PageIntro,
  StatusBadge,
  Toast,
} from '../components/ui.jsx'
import { useRemote } from '../hooks/useRemote.js'
import { api } from '../services/api.js'
import { BoxForm } from './Resources.jsx'

export default function BoxDetail() {
  const { id } = useParams(),
    auth = useAuth(),
    navigate = useNavigate()
  const resource = useRemote(`/boxes/${id}/`),
    [edit, setEdit] = useState(false),
    [action, setAction] = useState(''),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(null),
    [toast, setToast] = useState('')
  if (resource.loading) return <LoadingState label="Consultando la caja…" />
  if (resource.error)
    return (
      <>
        <PageIntro
          eyebrow="CONSULTA DE CAJA"
          title={
            resource.error.status === 404 ? 'Caja no disponible.' : 'No pudimos consultar la caja.'
          }
        >
          El registro puede no existir o no estar disponible para tu empresa.
        </PageIntro>
        <ErrorState error={resource.error} onRetry={resource.reload} />
        <Link className="text-link" to="/app/cajas">
          Volver a cajas
        </Link>
      </>
    )
  const box = resource.data,
    mutable = box.status === 'REGISTERED'
  async function execute() {
    setBusy(true)
    setError(null)
    try {
      await api(`/boxes/${id}/`, {
        method: action === 'delete' ? 'DELETE' : 'PATCH',
        ...(action !== 'delete' ? { data: { status: action } } : {}),
      })
      if (action === 'delete') navigate('/app/cajas')
      else {
        setAction('')
        resource.reload()
        setToast('Estado actualizado.')
      }
    } catch (error) {
      setError(error)
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <Link className="text-link back-link" to="/app/cajas">
        <Icon name="arrow" className="rotate-arrow" />
        Volver a cajas
      </Link>
      <PageIntro
        eyebrow="IDENTIFICACIÓN / CONTEXTO / ESTADO"
        title="Detalle de caja"
        action={
          mutable && (
            <Button variant="dark" onClick={() => setEdit(true)}>
              <Icon name="edit" />
              Editar caja
            </Button>
          )
        }
      >
        {box.company_name} · {box.branch_name}
      </PageIntro>
      <div className="box-detail-grid">
        <section className="identity-panel">
          <p className="eyebrow">IDENTIFICADOR INTERNO</p>
          <h2 className="mono">{box.internal_id}</h2>
          <StatusBadge value={box.status} />
          <div className="qr-content">
            <p className="eyebrow">CÓDIGO QR / CONTENIDO</p>
            <code>{box.qr_code}</code>
            <p>
              Identificador independiente. Si el QR se daña, utiliza el ID interno para consultar
              esta caja.
            </p>
          </div>
          <p className="small-note">
            La lectura mediante cámara se incorporará en una fase posterior.
          </p>
        </section>
        <section className="detail-panel">
          <h2>Datos de la mercancía</h2>
          <dl>
            {[
              ['Producto', box.product_name],
              ['SKU', box.product_sku],
              ['Categoría', box.category_name],
              ['Cantidad', box.quantity],
              ['Peso (kg)', box.weight_kg || 'No registrado'],
              ['Sucursal', box.branch_name],
              ['Prioridad', <StatusBadge value={box.priority} />],
              ['Creación', new Date(box.created_at).toLocaleString('es-PE')],
            ].map(([term, value]) => (
              <div key={term}>
                <dt>{term}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </section>
      </div>
      <section className="record-actions">
        <div>
          <h2>{mutable ? 'Actualizar el estado inicial' : 'Estado final protegido'}</h2>
          <p>
            {mutable
              ? 'Estas marcas no sustituyen un proceso de recepción avanzada. El cambio a un estado final no se puede revertir en este alcance.'
              : 'Esta caja ya no admite edición ni eliminación. Puedes seguir consultando sus datos.'}
          </p>
        </div>
        {mutable && (
          <div className="action-buttons">
            <Button
              variant="secondary"
              onClick={() => {
                setError(null)
                setAction('RECEIVED')
              }}
            >
              Marcar recibida
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                setError(null)
                setAction('REJECTED')
              }}
            >
              Marcar rechazada
            </Button>
            {auth.user.role !== 'OPERATOR' && (
              <Button
                variant="text"
                className="danger-text"
                onClick={() => {
                  setError(null)
                  setAction('delete')
                }}
              >
                Eliminar caja
              </Button>
            )}
          </div>
        )}
      </section>
      {edit && (
        <BoxForm
          record={box}
          onClose={() => setEdit(false)}
          onSaved={(message) => {
            setEdit(false)
            setToast(message)
            resource.reload()
          }}
        />
      )}
      {action === 'delete' && (
        <ConfirmModal
          title="Eliminar caja"
          onClose={() => setAction('')}
          onConfirm={execute}
          busy={busy}
          error={error}
        >
          Se eliminará la caja {box.internal_id}. Esta acción no se puede deshacer.
        </ConfirmModal>
      )}
      {action && action !== 'delete' && (
        <Modal title="Confirmar cambio de estado" onClose={() => setAction('')} busy={busy}>
          <div className="modal-body">
            <p>
              La caja quedará <strong>{action === 'RECEIVED' ? 'recibida' : 'rechazada'}</strong> y
              no admitirá nuevos cambios de datos en este CRUD.
            </p>
            {error && <ErrorState error={error} />}
          </div>
          <footer>
            <Button variant="secondary" disabled={busy} onClick={() => setAction('')}>
              Cancelar
            </Button>
            <Button variant="dark" busy={busy} onClick={execute}>
              Confirmar estado
            </Button>
          </footer>
        </Modal>
      )}
      {toast && <Toast message={toast} onClose={() => setToast('')} />}
    </>
  )
}
