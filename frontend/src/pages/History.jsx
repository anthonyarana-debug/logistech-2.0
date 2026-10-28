import { useSearchParams } from 'react-router-dom'
import { useTenant } from '../components/AppShell.jsx'
import { DataTable, EmptyState, ErrorState, FormField, LoadingState, PageIntro, StatusBadge } from '../components/ui.jsx'
import { useDebounced, useRemote } from '../hooks/useRemote.js'
import { t, formatDate } from '../i18n/index.js'

function EventDetails({ event }) {
  const data = event.data || {}
  const fields = [
    [t('quantity'), data.quantity ?? t('not_recorded')],
    [t('weight_kg'), data.weight_kg ?? t('not_recorded')],
    [t('priority'), data.priority ? <StatusBadge value={data.priority} /> : t('not_recorded')],
    [t('trace_result'), <StatusBadge value={data.result || data.status || event.outcome} />],
    [t('trace_reason'), data.reason ? t(`trace_reason_${data.reason}`) : t('trace_no_reason')],
    ...(data.source ? [[t('trace_source'), t(`trace_source_${data.source}`)]] : []),
    ...(data.receipt ? [[t('trace_receipt_id'), data.receipt]] : []),
    ...(data.product ? [[t('trace_product_id'), data.product]] : []),
    ...(data.branch ? [[t('trace_branch_id'), data.branch]] : []),
  ]
  return <details>
    <summary style={{ cursor: 'pointer' }}>{t('trace_event_data')}</summary>
    <dl style={{ minWidth: 180, maxWidth: 280, marginTop: 16, whiteSpace: 'normal' }}>
      {fields.map(([label, value]) => <div key={label} style={{ marginBottom: 12 }}>
        <dt style={{ fontWeight: 600 }}>{label}</dt>
        <dd style={{ margin: '4px 0 0', overflowWrap: 'anywhere' }}>{value}</dd>
      </div>)}
    </dl>
  </details>
}

export default function History() {
  const tenant = useTenant(), [params, setParams] = useSearchParams()
  const box = params.get('box') || '', filter = useDebounced(box)
  const events = useRemote('/box-events/', { company: tenant.company, box: filter })
  return <>
    <PageIntro eyebrow={t('trace_operations')} title={t('trace_history')}>{t('trace_history_description')}</PageIntro>
    <FormField label={t('trace_box_filter')} value={box} onChange={e => setParams(e.target.value ? { box: e.target.value } : {}, { replace: true })} maxLength={36} />
    {events.loading ? <LoadingState /> : events.error ? <ErrorState error={events.error} onRetry={events.reload} /> : !events.data.length ?
      <EmptyState title={t('trace_no_events')}>{t('trace_no_events_hint')}</EmptyState> :
      <DataTable caption={t('trace_history')} rows={events.data} columns={[
        { key: 'created_at', title: t('created'), render: r => formatDate(r.created_at) },
        { key: 'event_type', title: t('trace_event'), render: r => t(`trace_event_${r.event_type}`) },
        { key: 'internal_id', title: t('internal_identifier'), render: r => <span className="mono" style={{ display: 'block', maxWidth: '19ch', overflowWrap: 'anywhere', whiteSpace: 'normal' }}>{r.internal_id}</span> },
        { key: 'actor', title: t('trace_actor'), render: r => <span className="mono" style={{ display: 'block', maxWidth: '18ch', overflowWrap: 'anywhere', whiteSpace: 'normal' }}>{r.actor}</span> },
        { key: 'outcome', title: t('trace_result'), render: r => <StatusBadge value={r.outcome} /> },
        { key: 'data', title: t('trace_event_data'), render: r => <EventDetails event={r} /> },
      ]} />}
  </>
}
