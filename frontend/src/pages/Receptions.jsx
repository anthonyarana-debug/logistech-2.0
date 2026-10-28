import { useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useTenant } from '../components/AppShell.jsx'
import { Button, DataTable, EmptyState, ErrorState, LoadingState, PageIntro, SelectField, StatusBadge } from '../components/ui.jsx'
import { useRemote } from '../hooks/useRemote.js'
import { t, formatDate } from '../i18n/index.js'
import { api } from '../services/api.js'
import { receiptAttempt, receiptBody } from '../services/traceability.js'
import { CodeLookup } from './Identification.jsx'

function ReceiptForm({ box, onSaved }) {
  const [result, setResult] = useState('RECEIVED'), [reason, setReason] = useState('')
  const [busy, setBusy] = useState(false), [error, setError] = useState(null), [saved, setSaved] = useState(false)
  const attempt = useRef(null)
  async function save(event) {
    event.preventDefault(); setBusy(true); setError(null)
    attempt.current = receiptAttempt(attempt.current, receiptBody(box, result, reason))
    try {
      await api('/receipts/', { method: 'POST', data: attempt.current.data, headers: { 'Idempotency-Key': attempt.current.key } })
      setSaved(true); onSaved()
    } catch (error) { setError(error) } finally { setBusy(false) }
  }
  return <section className="detail-panel"><h2>{box.internal_id}</h2><p>{box.product_name} · {box.branch_name}</p>
    <div className="action-buttons">
      <Link className="text-link" to={`/app/cajas/${box.id}`}>{t('box_details')}</Link>
      <Link className="text-link" to={`/app/history?box=${box.id}`}>{t('trace_history')}</Link>
    </div>
    {saved ? <p role="status">{t('trace_receipt_saved')}</p> : box.status !== 'REGISTERED' ? <p>{t('trace_terminal')}</p> :
      <form onSubmit={save}>
        <SelectField label={t('trace_result')} value={result} disabled={busy} onChange={e => { setResult(e.target.value); setError(null) }} required
          options={['RECEIVED', 'REJECTED'].map(id => ({ id, name: t(id === 'RECEIVED' ? 'received' : 'rejected') }))} />
        {result === 'REJECTED' && <SelectField label={t('trace_reason')} value={reason} disabled={busy} onChange={e => setReason(e.target.value)} required
          options={['DAMAGED', 'INCORRECT_ITEM', 'OTHER'].map(id => ({ id, name: t(`trace_reason_${id}`) }))} />}
        <p>{t('trace_receipt_policy')}</p>
        {error && <ErrorState error={error} />}
        {error?.status === 0 && <p>{t('trace_retry_policy')}</p>}
        <Button variant="dark" busy={busy}>{t('trace_save_receipt')}</Button>
      </form>}
  </section>
}
export default function Receptions() {
  const tenant = useTenant(), [params] = useSearchParams(), [selected, setSelected] = useState(undefined)
  const initial = useRemote(`/boxes/${params.get('box')}/`, {}, !!params.get('box'))
  const receipts = useRemote('/receipts/', { company: tenant.company })
  const box = selected === undefined ? initial.data : selected
  return <>
    <PageIntro eyebrow={t('trace_operations')} title={t('receptions')}>{t('trace_reception_description')}</PageIntro>
    <div className="box-detail-grid"><CodeLookup onResolved={setSelected} />
      {selected === undefined && initial.loading ? <LoadingState /> : selected === undefined && initial.error ? <ErrorState error={initial.error} /> : box && <ReceiptForm key={box.id} box={box} onSaved={receipts.reload} />}</div>
    <h2>{t('trace_receipt_records')}</h2>
    {receipts.loading ? <LoadingState /> : receipts.error ? <ErrorState error={receipts.error} onRetry={receipts.reload} /> : !receipts.data.length ?
      <EmptyState title={t('trace_no_receipts')}>{t('trace_no_receipts_hint')}</EmptyState> :
      <DataTable caption={t('trace_receipt_records')} rows={receipts.data} columns={[
        { key: 'internal_id', title: t('internal_identifier'), render: r => <Link className="text-link" to={`/app/cajas/${r.box}`}>{r.internal_id}</Link> },
        { key: 'result', title: t('trace_result'), render: r => <StatusBadge value={r.result} /> },
        { key: 'reason', title: t('trace_reason'), render: r => r.reason ? t(`trace_reason_${r.reason}`) : '—' },
        { key: 'actor', title: t('trace_actor') },
        { key: 'created_at', title: t('created'), render: r => formatDate(r.created_at) },
      ]} />}
  </>
}
