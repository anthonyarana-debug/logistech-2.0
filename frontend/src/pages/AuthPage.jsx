import { t } from '../i18n/index.js'
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
      setError(new Error(t("passwords_do_not_match")))
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
        <Link to="/" aria-label={t("back_to_home")}>
          <Logo />
        </Link>
        <div>
          <p className="eyebrow">{t("identify_organize_control")}</p>
          <h2>{t("the_right")}<br />{t("information")}<br />
            <em>{t("in_your_hands")}</em>
          </h2>
          <div className="tracking-lines" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
            <span />
            <span />
          </div>
          <p>{t("an_identity_for_every_box")}<br />{t("a_workspace_for_every_company")}</p>
        </div>
        <p className="auth-brand-footer">{t("logistech_logistics_platform")}</p>
      </aside>
      <section className="auth-content">
        <Link className="auth-back text-link" to="/">
          <Icon name="arrow" className="rotate-arrow" />{' '}{t("back_to_home")}</Link>
        <div className="auth-form-wrap">
          <p className="eyebrow">{t("your_workspace")}</p>
          <h1>
            {success ? t("your_account_has_been_created") : signup ? t("it_starts_with_you") : t("welcome_back")}
          </h1>
          <p className="auth-lead">
            {success
              ? t("your_operator_account_is_awaiting_company_assignment_you")
              : signup
                ? t("register_as_an_operator_a_superadmin_will_assign")
                : t("sign_in_to_continue_your_operations")}
          </p>
          {success ? (
            <Link className="button button-dark" to="/login">{t("go_to_sign_in")}{' '}<Icon name="arrow" />
            </Link>
          ) : (
            <form
              onSubmit={submit}
              aria-label={signup ? t("registration_form") : t("sign_in_form")}
            >
              {error && <ErrorState error={error} />}
              {signup && (
                <FormField
                  label={t("first_name")}
                  name="first_name"
                  autoComplete="given-name"
                  maxLength={150}
                  required
                />
              )}
              <FormField
                label={t("email_address")}
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
                    ? t("at_least_12_characters_avoid_common_passwords_numbers")
                    : undefined
                }
              />
              {signup && (
                <PasswordField
                  label={t("confirm_password")}
                  name="confirmation"
                  autoComplete="new-password"
                  minLength={12}
                  maxLength={128}
                  required
                />
              )}
              <Button variant="dark" type="submit" busy={busy} className="full-width">
                {signup ? t("create_operator_account") : t("sign_in")}
                <Icon name="arrow" />
              </Button>
              <p className="auth-switch">
                {signup ? t("already_have_an_account") : t("new_here")}{' '}
                <Link to={signup ? '/login' : '/registro'}>
                  {signup ? t("sign_in") : t("create_your_account")}
                </Link>
              </p>
            </form>
          )}
          <div className="auth-assurance">
            <Icon name="check" />
            <p>{t("protected_session_information_access_depends_on_your_role")}</p>
          </div>
        </div>
        <p className="auth-footnote">{t("logistech_2_0_cloud_solutions_development")}</p>
      </section>
    </main>
  )
}
