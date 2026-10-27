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

export default function Dashboard() {
  const auth = useAuth(),
    tenant = useTenant()
  const boxes = useRemote('/boxes/', { company: tenant.company }),
    cats = useRemote('/categories/', { company: tenant.company })
  return (
    <>
      <PageIntro
        eyebrow="TU HOJA DE CONTROL"
        title={`Todo en su contexto${auth.user.first_name ? `, ${auth.user.first_name}` : ''}.`}
        action={
          <Link to="/app/cajas" className="button button-dark">
            Ir a cajas <Icon name="arrow" />
          </Link>
        }
      >
        Consulta el estado de los registros del ámbito seleccionado. Los indicadores se calculan con
        las respuestas actuales de la API.
      </PageIntro>
      {boxes.error || cats.error ? (
        <ErrorState
          error={boxes.error || cats.error}
          onRetry={() => {
            boxes.reload()
            cats.reload()
          }}
        />
      ) : boxes.loading || cats.loading ? (
        <LoadingState />
      ) : (
        <>
          <section className="overview-strip" aria-label="Resumen de la consulta">
            <div>
              <span className="mono">CAJAS EN ESTE ÁMBITO</span>
              <strong>{boxes.data.length.toLocaleString('es-PE')}</strong>
              <p>Registros disponibles</p>
            </div>
            <div>
              <span className="mono">POR ESTADO INICIAL</span>
              <strong>
                {boxes.data.filter((b) => b.status === 'REGISTERED').length.toLocaleString('es-PE')}
              </strong>
              <p>En estado registrada</p>
            </div>
            <div>
              <span className="mono">CLASIFICACIÓN</span>
              <strong>{cats.data.length.toLocaleString('es-PE')}</strong>
              <p>Categorías disponibles</p>
            </div>
          </section>
          <p className="scope-note">
            Ámbito: {tenant.companyName}. Conteos de registros, no unidades de stock ni métricas
            históricas.
          </p>
          <section className="workspace-section">
            <div className="section-top">
              <div>
                <p className="eyebrow">CONSULTA OPERACIONAL</p>
                <h2>Últimos registros</h2>
              </div>
              <Link className="text-link" to="/app/cajas">
                Ver todas las cajas <Icon name="arrow" />
              </Link>
            </div>
            {boxes.data.length ? (
              <DataTable
                caption="Últimas cinco cajas por fecha de creación"
                rows={[...boxes.data].reverse().slice(0, 5)}
                columns={[
                  {
                    key: 'internal_id',
                    title: 'Identificador',
                    render: (b) => (
                      <Link className="mono id-link" to={`/app/cajas/${b.id}`}>
                        {b.internal_id}
                      </Link>
                    ),
                  },
                  { key: 'product_name', title: 'Producto' },
                  { key: 'branch_name', title: 'Sucursal' },
                  {
                    key: 'status',
                    title: 'Estado',
                    render: (b) => <StatusBadge value={b.status} />,
                  },
                ]}
              />
            ) : (
              <EmptyState
                title="El orden empieza con la primera caja"
                action={
                  <Link className="button button-secondary" to="/app/cajas">
                    Gestionar cajas
                  </Link>
                }
              >
                Los registros aparecerán aquí cuando se creen cajas autorizadas.
              </EmptyState>
            )}
          </section>
        </>
      )}
      <section className="work-note">
        <Icon name="tag" />
        <div>
          <h2>Clasificar también es cuidar.</h2>
          <p>
            Las categorías permiten distinguir mercancía frágil y perecedera. Consulta sus
            condiciones antes de registrar una caja.
          </p>
        </div>
        <Link to="/app/categorias" className="text-link">
          Ver categorías <Icon name="arrow" />
        </Link>
      </section>
    </>
  )
}
