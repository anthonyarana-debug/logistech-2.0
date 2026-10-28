import { t, formatDate } from '../i18n/index.js'
import { useEffect, useState } from 'react'
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
import { downloadLabel } from '../services/traceability.js'
import { BoxForm } from './Resources.jsx'

function BoxIdentity({ box }) {
  const qr = useRemote(`/boxes/${box.id}/qr/`)
  const [url, setUrl] = useState(''), [error, setError] = useState(null), [busy, setBusy] = useState(false)
  useEffect(() => {
    if (!qr.data?.svg) return
    const objectUrl = URL.createObjectURL(new globalThis.Blob([qr.data.svg], { type: 'image/svg+xml' }))
    setUrl(objectUrl)
    return () => URL.revokeObjectURL(objectUrl)
  }, [qr.data])
  async function download() {
    setBusy(true); setError(null)
    try { await downloadLabel(box.id, box.internal_id) } catch (error) { setError(error) } finally { setBusy(false) }
  }
  return <div className="qr-content">
    <p className="eyebrow">{t('qr_code_content')}</p>
    {qr.loading ? <LoadingState /> : qr.error ? <ErrorState error={qr.error} onRetry={qr.reload} /> : <>
      {url && <img src={url} alt={t('trace_qr_alt', { identifier: box.internal_id })} width="200" height="200" style={{ maxWidth: '100%' }} />}
      <p><code style={{ overflowWrap: 'anywhere' }}>{qr.data.payload}</code></p>
      <Button variant="secondary" busy={busy} onClick={download}>{t('trace_download_label')}</Button>
    </>}
    {error && <ErrorState error={error} />}
    <p>{t('independent_identifier_if_the_qr_code_is_damaged')}</p>
    <div className="action-buttons">
      <Link className="text-link" to={`/app/receptions?box=${box.id}`}>{t('receptions')}</Link>
      <Link className="text-link" to={`/app/history?box=${box.id}`}>{t('trace_history')}</Link>
    </div>
  </div>
}

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
  if (resource.loading) return <LoadingState label={t("loading_box")} />
  if (resource.error)
    return (
      <>
        <PageIntro
          eyebrow={t("box_lookup")}
          title={
            resource.error.status === 404 ? t("box_unavailable") : t("we_could_not_retrieve_the_box")
          }
        >{t("the_record_may_not_exist_or_may_be")}</PageIntro>
        <ErrorState error={resource.error} onRetry={resource.reload} />
        <Link className="text-link" to="/app/cajas">{t("back_to_boxes")}</Link>
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
        setToast(t("status_updated"))
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
        <Icon name="arrow" className="rotate-arrow" />{t("back_to_boxes")}</Link>
      <PageIntro
        eyebrow={t("identification_context_status")}
        title={t("box_details")}
        action={
          mutable && (
            <Button variant="dark" onClick={() => setEdit(true)}>
              <Icon name="edit" />{t("edit_box")}</Button>
          )
        }
      >
        {box.company_name} · {box.branch_name}
      </PageIntro>
      <div className="box-detail-grid">
        <section className="identity-panel">
          <p className="eyebrow">{t("internal_identifier")}</p>
          <h2 className="mono">{box.internal_id}</h2>
          <StatusBadge value={box.status} />
          <BoxIdentity key={box.id} box={box} />
        </section>
        <section className="detail-panel">
          <h2>{t("goods_details")}</h2>
          <dl>
            {[
              [t("product"), box.product_name],
              ['SKU', box.product_sku],
              [t("category"), box.category_name],
              [t("quantity"), box.quantity],
              [t("weight_kg"), box.weight_kg || t("not_recorded")],
              [t("branch"), box.branch_name],
              [t("priority"), <StatusBadge value={box.priority} />],
              [t("created"), formatDate(box.created_at)],
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
          <h2>{mutable ? t("update_the_initial_status") : t("final_status_protected")}</h2>
          <p>
            {mutable
              ? t("these_labels_do_not_replace_an_advanced_reception")
              : t("this_box_can_no_longer_be_edited_or")}
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
            >{t("mark_as_received")}</Button>
            <Button
              variant="secondary"
              onClick={() => {
                setError(null)
                setAction('REJECTED')
              }}
            >{t("mark_as_rejected")}</Button>
            {auth.user.role !== 'OPERATOR' && (
              <Button
                variant="text"
                className="danger-text"
                onClick={() => {
                  setError(null)
                  setAction('delete')
                }}
              >{t("delete_box")}</Button>
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
          title={t("delete_box")}
          onClose={() => setAction('')}
          onConfirm={execute}
          busy={busy}
          error={error}
        >{t("this_box_will_be_deleted")}{' '}{box.internal_id}{t("this_action_cannot_be_undone")}</ConfirmModal>
      )}
      {action && action !== 'delete' && (
        <Modal title={t("confirm_status_change")} onClose={() => setAction('')} busy={busy}>
          <div className="modal-body">
            <p>{t("the_box_will_be_marked")}{' '}<strong>{action === 'RECEIVED' ? t("received_2") : t("rejected_2")}</strong>{' '}{t("and_will_no_longer_accept_data_changes_in")}</p>
            {error && <ErrorState error={error} />}
          </div>
          <footer>
            <Button variant="secondary" disabled={busy} onClick={() => setAction('')}>{t("cancel")}</Button>
            <Button variant="dark" busy={busy} onClick={execute}>{t("confirm_status")}</Button>
          </footer>
        </Modal>
      )}
      {toast && <Toast message={toast} onClose={() => setToast('')} />}
    </>
  )
}
