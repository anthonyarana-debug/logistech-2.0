import { t } from '../i18n/index.js'
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
          {forbidden ? t("this_access_is_unavailable_to_you") : t("this_route_has_no_destination")}
        </h1>
        <p>
          {forbidden
            ? t("your_role_or_assignment_does_not_allow_access")
            : t("check_the_address_or_return_to_a_familiar")}
        </p>
        <div className="action-buttons">
          <Link className="button button-dark" to="/app">{t("go_to_my_workspace")}{' '}<Icon name="arrow" />
          </Link>
          <Link className="text-link" to="/">{t("back_to_home")}</Link>
        </div>
      </main>
    </>
  )
}
export function InDevelopment() {
  return (
    <>
      <PageIntro
        eyebrow={t("roadmap_future_features")}
        title={t("the_next_stage_is_in_development")}
      />
      <EmptyState title={t("advanced_reception_in_a_future_phase")}>{t("camera_and_qr_scanning_reception_events_history_and")}</EmptyState>
      <Link className="button button-secondary" to="/app/cajas">{t("view_available_boxes")}</Link>
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
        <p className="eyebrow">{t("service_availability")}</p>
        <h1>{t("a_connection_you_can_verify")}</h1>
        <p>{t("check_the_api_and_postgresql_right_now_historical")}</p>
        {state.status === 'loading' ? (
          <LoadingState />
        ) : state.status === 'ready' ? (
          <p className="success-note" role="status">
            <Icon name="check" />{t("api_and_postgresql_are_available")}</p>
        ) : state.status === 'error' ? (
          <ErrorState error={state.error} />
        ) : null}
        <Button variant="dark" busy={state.status === 'loading'} onClick={check}>{t("check_service")}</Button>
      </main>
    </>
  )
}
