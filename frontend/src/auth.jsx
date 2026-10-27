import { createContext, useContext, useEffect, useState, useSyncExternalStore } from 'react'
import { Link, Navigate } from 'react-router-dom'
import * as session from './services/api.js'
import { Button, EmptyState, ErrorState, LoadingState, Logo } from './components/ui.jsx'

const Context = createContext(null)
export function AuthProvider({ children }) {
  const state = useSyncExternalStore(session.subscribe, session.snapshot)
  useEffect(() => {
    session.restore()
  }, [])
  return (
    <Context.Provider
      value={{
        ...state,
        login: session.login,
        logout: session.logout,
        updateProfile: session.updateProfile,
      }}
    >
      {children}
    </Context.Provider>
  )
}
export function useAuth() {
  return useContext(Context)
}
export function SessionExpired() {
  return (
    <main className="standalone">
      <Logo />
      <EmptyState
        title="Tu sesión ha expirado"
        action={
          <Link className="button button-primary" to="/login">
            Volver a iniciar sesión
          </Link>
        }
      >
        Por seguridad, vuelve a identificarte para continuar. No se muestran datos privados.
      </EmptyState>
    </main>
  )
}
export function Protected({ children }) {
  const auth = useAuth()
  if (auth.status === 'loading')
    return (
      <main className="standalone">
        <Logo />
        <LoadingState label="Restaurando sesión de forma segura…" />
      </main>
    )
  if (auth.status === 'error')
    return (
      <main className="standalone">
        <Logo />
        <ErrorState
          error={auth.error}
          title={
            auth.reason === 'logout-pending'
              ? 'El cierre de sesión no pudo confirmarse'
              : 'No pudimos restaurar tu sesión'
          }
          onRetry={() => session.restore(true)}
        />
        <Link to="/login">Ir al inicio de sesión</Link>
      </main>
    )
  if (!auth.user)
    return auth.reason === 'expired' ? <SessionExpired /> : <Navigate to="/login" replace />
  if (auth.user.assignment_pending)
    return (
      <main className="standalone">
        <Logo />
        <EmptyState title="Tu cuenta está lista. Falta una asignación.">
          Eres operador y todavía no tienes una empresa asignada. Un superadministrador debe
          habilitar tu acceso al inventario.
        </EmptyState>
        <p className="identity-line">{auth.user.email}</p>
        <AssignmentActions />
      </main>
    )
  return children
}
function AssignmentActions() {
  const auth = useAuth()
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(null)
  async function check() {
    setBusy(true)
    setError(null)
    try {
      await auth.updateProfile()
    } catch (err) {
      setError(err)
    } finally {
      setBusy(false)
    }
  }
  return (
    <>
      <div className="standalone-actions">
        <Button variant="secondary" busy={busy} onClick={check}>
          Comprobar asignación
        </Button>
        <Button variant="text" disabled={busy} onClick={() => auth.logout().catch(() => {})}>
          Cerrar sesión
        </Button>
      </div>
      {error && <ErrorState error={error} />}
    </>
  )
}
