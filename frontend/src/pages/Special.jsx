import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Button,
  EmptyState,
  ErrorState,
  Icon,
  LoadingState,
  Logo,
  PageIntro,
  PublicHeader,
} from '../components/ui.jsx'
import { getHealth } from '../services/health.js'

export function NotFound({ forbidden = false }) {
  return (
    <>
      <PublicHeader />
      <main className="special-page">
        <span className="error-code mono">{forbidden ? '403' : '404'}</span>
        <h1>
          {forbidden ? 'Este acceso no está disponible para ti.' : 'Esta ruta no tiene destino.'}
        </h1>
        <p>
          {forbidden
            ? 'Tu rol o asignación no permite consultar este recurso. La autorización se verifica en el servidor.'
            : 'Revisa la dirección o vuelve a un lugar conocido.'}
        </p>
        <div className="action-buttons">
          <Link className="button button-dark" to="/app">
            Ir a mi espacio <Icon name="arrow" />
          </Link>
          <Link className="text-link" to="/">
            Volver al inicio
          </Link>
        </div>
      </main>
    </>
  )
}
export function InDevelopment() {
  return (
    <>
      <PageIntro
        eyebrow="HOJA DE RUTA / FUNCIONES FUTURAS"
        title="El siguiente tramo está en desarrollo."
      />
      <EmptyState title="Recepción avanzada, en una próxima fase">
        Cámara y escaneo QR, eventos de recepción, historial y reportes requieren funcionalidades de
        fases posteriores. Las marcas de estado actuales no equivalen a ese proceso.
      </EmptyState>
      <Link className="button button-secondary" to="/app/cajas">
        Consultar cajas disponibles
      </Link>
    </>
  )
}
export function ServiceStatus() {
  const [state, setState] = useState({ status: 'idle' })
  async function check() {
    setState({ status: 'loading' })
    try {
      await getHealth()
      setState({ status: 'ready' })
    } catch (error) {
      setState({ status: 'error', error })
    }
  }
  return (
    <>
      <PublicHeader />
      <main className="standalone">
        <Logo />
        <p className="eyebrow">DISPONIBILIDAD DEL SERVICIO</p>
        <h1>Una conexión comprobable.</h1>
        <p>
          Consulta la API y PostgreSQL en este momento. No se presentan mediciones de disponibilidad
          histórica.
        </p>
        {state.status === 'loading' ? (
          <LoadingState />
        ) : state.status === 'ready' ? (
          <p className="success-note" role="status">
            <Icon name="check" />
            API y PostgreSQL disponibles.
          </p>
        ) : state.status === 'error' ? (
          <ErrorState error={state.error} />
        ) : null}
        <Button variant="dark" busy={state.status === 'loading'} onClick={check}>
          Comprobar servicio
        </Button>
      </main>
    </>
  )
}
