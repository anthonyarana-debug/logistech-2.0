import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth.jsx'
import { register } from '../services/api.js'
import { Button, ErrorState, FormField, Icon, Logo, PasswordField } from '../components/ui.jsx'

export default function AuthPage({ signup = false }) {
  const auth = useAuth(),
    navigate = useNavigate()
  const [error, setError] = useState(null),
    [busy, setBusy] = useState(false),
    [success, setSuccess] = useState(false)
  if (auth.user) return <Navigate to="/app" replace />
  async function submit(event) {
    event.preventDefault()
    setError(null)
    const data = Object.fromEntries(new FormData(event.currentTarget))
    if (signup && data.password !== data.confirmation) {
      setError(new Error('Las contraseñas no coinciden.'))
      return
    }
    delete data.confirmation
    setBusy(true)
    try {
      if (signup) {
        await register(data)
        setSuccess(true)
      } else {
        await auth.login(data)
        navigate('/app', { replace: true })
      }
    } catch (error) {
      setError(error)
    } finally {
      setBusy(false)
    }
  }
  return (
    <main className="auth-layout">
      <aside className="auth-brand">
        <Link to="/" aria-label="Volver al inicio">
          <Logo />
        </Link>
        <div>
          <p className="eyebrow">IDENTIFICA. ORGANIZA. CONTROLA.</p>
          <h2>
            La información
            <br />
            correcta.
            <br />
            <em>En tus manos.</em>
          </h2>
          <div className="tracking-lines" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
            <span />
            <span />
          </div>
          <p>
            Una identidad para cada caja.
            <br />
            Un espacio para cada empresa.
          </p>
        </div>
        <p className="auth-brand-footer">LOGISTECH / PLATAFORMA LOGÍSTICA</p>
      </aside>
      <section className="auth-content">
        <Link className="auth-back text-link" to="/">
          <Icon name="arrow" className="rotate-arrow" /> Volver al inicio
        </Link>
        <div className="auth-form-wrap">
          <p className="eyebrow">TU ESPACIO DE TRABAJO</p>
          <h1>
            {success ? 'Tu cuenta está creada.' : signup ? 'Empezamos por ti.' : 'Qué bueno verte.'}
          </h1>
          <p className="auth-lead">
            {success
              ? 'Tu cuenta de operador está pendiente de asignación a una empresa. Ya puedes iniciar sesión.'
              : signup
                ? 'Regístrate como operador. Un superadministrador asignará tu empresa antes de acceder al inventario.'
                : 'Inicia sesión para continuar con tus operaciones.'}
          </p>
          {success ? (
            <Link className="button button-dark" to="/login">
              Ir a iniciar sesión <Icon name="arrow" />
            </Link>
          ) : (
            <form
              onSubmit={submit}
              aria-label={signup ? 'Formulario de registro' : 'Formulario de inicio de sesión'}
            >
              {error && <ErrorState error={error} />}
              {signup && (
                <FormField
                  label="Nombre"
                  name="first_name"
                  autoComplete="given-name"
                  maxLength={150}
                  required
                />
              )}
              <FormField
                label="Correo electrónico"
                name="email"
                type="email"
                autoComplete="username"
                maxLength={254}
                required
              />
              <PasswordField
                name="password"
                autoComplete={signup ? 'new-password' : 'current-password'}
                minLength={signup ? 12 : undefined}
                maxLength={128}
                required
                hint={
                  signup
                    ? 'Mínimo 12 caracteres. Evita contraseñas comunes, solo números o similares a tu correo.'
                    : undefined
                }
              />
              {signup && (
                <PasswordField
                  label="Confirmar contraseña"
                  name="confirmation"
                  autoComplete="new-password"
                  minLength={12}
                  maxLength={128}
                  required
                />
              )}
              <Button variant="dark" type="submit" busy={busy} className="full-width">
                {signup ? 'Crear cuenta de operador' : 'Iniciar sesión'}
                <Icon name="arrow" />
              </Button>
              <p className="auth-switch">
                {signup ? '¿Ya tienes una cuenta?' : '¿Es tu primera vez aquí?'}{' '}
                <Link to={signup ? '/login' : '/registro'}>
                  {signup ? 'Inicia sesión' : 'Crea tu cuenta'}
                </Link>
              </p>
            </form>
          )}
          <div className="auth-assurance">
            <Icon name="check" />
            <p>Sesión protegida. El acceso a la información depende de tu rol y tu empresa.</p>
          </div>
        </div>
        <p className="auth-footnote">LogisTech 2.0 · Desarrollo de Soluciones en la Nube</p>
      </section>
    </main>
  )
}
