import { t } from './i18n/index.js'
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
        title={t("your_session_has_expired")}
        action={
          <Link className="button button-primary" to="/login">{t("sign_in_again")}</Link>
        }
      >{t("for_your_security_sign_in_again_to_continue")}</EmptyState>
    </main>
  )
}
export function Protected({ children }) {
  const auth = useAuth()
  if (auth.status === 'loading')
    return (
      <main className="standalone">
        <Logo />
        <LoadingState label={t("restoring_your_session_securely")} />
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
              ? t("sign_out_could_not_be_confirmed")
              : t("we_could_not_restore_your_session")
          }
          onRetry={() => session.restore(true)}
        />
        <Link to="/login">{t("go_to_sign_in")}</Link>
      </main>
    )
  if (!auth.user)
    return auth.reason === 'expired' ? <SessionExpired /> : <Navigate to="/login" replace />
  if (auth.user.assignment_pending)
    return (
      <main className="standalone">
        <Logo />
        <EmptyState title={t("your_account_is_ready_assignment_pending")}>{t("you_are_an_operator_without_an_assigned_company")}</EmptyState>
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
        <Button variant="secondary" busy={busy} onClick={check}>{t("check_assignment")}</Button>
        <Button variant="text" disabled={busy} onClick={() => auth.logout().catch(() => {})}>{t("sign_out")}</Button>
      </div>
      {error && <ErrorState error={error} />}
    </>
  )
}
