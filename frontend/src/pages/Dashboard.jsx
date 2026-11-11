import { t, formatNumber } from '../i18n/index.js'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth.jsx'
import { useTenant } from '../components/AppShell.jsx'
import {
  DataTable,
  EmptyState,
  ErrorState,
  Icon,
  LoadingState,
  PageIntro,
  StatusBadge,
} from '../components/ui.jsx'
import { useRemote } from '../hooks/useRemote.js'
import { dashboardKey } from '../services/operations.js'

export default function Dashboard() {
  const auth = useAuth(),
    tenant = useTenant()
  const boxes = useRemote('/boxes/', { company: tenant.company, page_size: 5, order: 'newest' }),
    registered = useRemote('/boxes/', { company: tenant.company, status: 'REGISTERED', page_size: 1 })
  const overview = useRemote('/overview/', { company: tenant.company })
  return (
    <>
      <PageIntro
        eyebrow={t("your_control_sheet")}
        title={t(dashboardKey(auth.user.role))}
        action={
          <Link to="/app/cajas" className="button button-dark">{t("go_to_boxes")}{' '}<Icon name="arrow" />
          </Link>
        }
      >{t("view_records_in_the_selected_scope_indicators_are")}</PageIntro>
      {overview.data &&
        <section className="overview-strip" aria-label={t('ops_administration')}>
          {Object.entries(overview.data.counts).filter(([kind]) => !['boxes', 'categories'].includes(kind)).map(([kind, count]) =>
            <div key={kind}><span className="mono">{t(kind === 'receipts' ? 'receptions' : kind === 'events' ? 'trace_history' : `ops_${kind}`)}</span>
              <strong>{formatNumber(count)}</strong><Link className="text-link" to={`/app/${kind === 'receipts' ? 'receptions' : kind === 'events' ? 'history' : kind}`}>{t('ops_open_records')}</Link></div>)}
        </section>}
      {boxes.error || registered.error || overview.error ? (
        <ErrorState
          error={boxes.error || registered.error || overview.error}
          onRetry={() => {
            boxes.reload()
            registered.reload()
            overview.reload()
          }}
        />
      ) : boxes.loading || registered.loading || overview.loading ? (
        <LoadingState />
      ) : (
        <>
          <section className="overview-strip" aria-label={t("query_summary")}>
            <div>
              <span className="mono">{t("boxes_in_this_scope")}</span>
              <strong>{formatNumber(boxes.data.count)}</strong>
              <p>{t("available_records")}</p>
            </div>
            <div>
              <span className="mono">{t("by_initial_status")}</span>
              <strong>
                {formatNumber(registered.data.count)}
              </strong>
              <p>{t("with_registered_status")}</p>
            </div>
            <div>
              <span className="mono">{t("classification")}</span>
              <strong>{formatNumber(overview.data.counts.categories)}</strong>
              <p>{t("available_categories")}</p>
            </div>
          </section>
          <p className="scope-note">{t("scope")}{' '}{tenant.companyName}{t("record_counts_not_stock_units_or_historical_metrics")}</p>
          <section className="workspace-section">
            <div className="section-top">
              <div>
                <p className="eyebrow">{t("operational_lookup")}</p>
                <h2>{t("latest_records")}</h2>
              </div>
              <Link className="text-link" to="/app/cajas">{t("view_all_boxes")}{' '}<Icon name="arrow" />
              </Link>
            </div>
            {boxes.data.count ? (
              <DataTable
                caption={t("latest_five_boxes_by_creation_date")}
                rows={boxes.data.results}
                columns={[
                  {
                    key: 'internal_id',
                    title: t("identifier"),
                    render: (b) => (
                      <Link className="mono id-link" to={`/app/cajas/${b.id}`}>
                        {b.internal_id}
                      </Link>
                    ),
                  },
                  { key: 'product_name', title: t("product") },
                  { key: 'branch_name', title: t("branch") },
                  {
                    key: 'status',
                    title: t("status"),
                    render: (b) => <StatusBadge value={b.status} />,
                  },
                ]}
              />
            ) : (
              <EmptyState
                title={t("order_starts_with_the_first_box")}
                action={
                  <Link className="button button-secondary" to="/app/cajas">{t("manage_boxes")}</Link>
                }
              >{t("records_will_appear_here_when_authorized_boxes_are")}</EmptyState>
            )}
          </section>
        </>
      )}
      <section className="work-note">
        <Icon name="tag" />
        <div>
          <h2>{t("classification_is_also_care")}</h2>
          <p>{t("categories_identify_fragile_and_perishable_goods_check_their")}</p>
        </div>
        <Link to="/app/categorias" className="text-link">{t("view_categories")}{' '}<Icon name="arrow" />
        </Link>
      </section>
    </>
  )
}
