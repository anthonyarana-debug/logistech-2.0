import { t } from '../i18n/index.js'
import { createContext, useContext, useEffect, useRef, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth.jsx'
import { useRemote } from '../hooks/useRemote.js'
import { canAdminister } from '../services/operations.js'
import { Button, Icon, Logo, SelectField } from './ui.jsx'

const Tenant = createContext(null)
export const useTenant = () => useContext(Tenant)
export const roleNames = {
  SUPERADMIN: t("superadmin"),
  COMPANY_ADMIN: t("company_administrator"),
  OPERATOR: t("operator"),
}
const baseNavigation = [
  ['/app', 'grid', t("overview")],
  ['/app/cajas', 'box', t("boxes")],
  ['/app/categorias', 'tag', t("categories")],
]
export default function AppShell() {
  const auth = useAuth(),
    location = useLocation()
  const [company, setCompany] = useState(''),
    [menu, setMenu] = useState(false)
  const dialog = useRef(null),
    content = useRef(null)
  const global = auth.user.role === 'SUPERADMIN'
  const navigation = [...baseNavigation,
    ['/app/branches', 'grid', t('ops_branches')],
    ['/app/products', 'tag', t('ops_products')],
    ...(canAdminister(auth.user, 'companies') ? [['/app/companies', 'grid', t('ops_companies')]] : []),
    ...(canAdminister(auth.user, 'users') ? [['/app/users', 'grid', t('ops_users')]] : []),
  ]
  const refs = useRemote('/references/', { company: global ? company : '' })
  useEffect(() => {
    if (menu) dialog.current.showModal()
    else dialog.current?.close()
  }, [menu])
  useEffect(() => {
    setMenu(false)
    content.current?.focus()
  }, [location.pathname])
  const selected = global ? company : auth.user.company.id
  const companyName =
    refs.data?.companies.find((c) => c.id === selected)?.name ||
    (global ? t("all_companies") : auth.user.company.name)
  function sidebar(mobile = false) {
    return (
      <>
        <Link className="sidebar-brand" to="/app" aria-label={t("logistech_overview")}>
          <Logo compact />
        </Link>
        <p className="sidebar-section">{t("workspace")}</p>
        <nav aria-label={mobile ? t("mobile_navigation") : t("system_navigation")}>
          {navigation.map(([to, icon, text]) => (
            <NavLink key={to} to={to} end={to === '/app'} onClick={() => setMenu(false)}>
              <Icon name={icon} />
              {text}
              <span className="nav-active-mark" />
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-upcoming">
          <p className="sidebar-section">{t("coming_soon")}</p>
          <Link to="/app/en-desarrollo" onClick={() => setMenu(false)}>
            <Icon name="clock" />{t("receptions")}<span className="soon-label">{t('ops_planned')}</span>
          </Link>
        </div>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <p>{t("a_place_for_everything")}<br />
            <strong>{t("context_for_every_decision")}</strong>
          </p>
        </div>
      </>
    )
  }
  return (
    <Tenant.Provider
      value={{ company: global ? company : '', selected, companyName, global, refs, setCompany }}
    >
      <div className="app-layout">
        <a className="skip-link" href="#app-contenido">{t("skip_to_content")}</a>
        <aside className="sidebar">{sidebar()}</aside>
        <dialog
          className="mobile-sidebar"
          ref={dialog}
          onCancel={(event) => {
            event.preventDefault()
            setMenu(false)
          }}
        >
          <button
            className="icon-button close-menu"
            aria-label={t("close_menu")}
            onClick={() => setMenu(false)}
          >
            <Icon name="close" />
          </button>
          {sidebar(true)}
        </dialog>
        <div className="app-column">
          <header className="app-header">
            <button
              className="icon-button mobile-menu"
              aria-label={t("open_menu")}
              onClick={() => setMenu(true)}
            >
              <Icon name="menu" />
            </button>
            <div className="header-context">
              <span className="mono eyebrow">{t("company_context")}</span>
              <strong>{companyName}</strong>
            </div>
            <div className="header-user">
              <span className="avatar" aria-hidden="true">
                {(auth.user.first_name || auth.user.email)[0].toUpperCase()}
              </span>
              <div>
                <strong>{auth.user.first_name || auth.user.email.split('@')[0]}</strong>
                <span>{roleNames[auth.user.role]}</span>
              </div>
              <button
                className="icon-button"
                onClick={() => auth.logout().catch(() => {})}
                aria-label={t("sign_out")}
              >
                <Icon name="logout" />
              </button>
            </div>
          </header>
          <div className="context-bar">
            <span className="context-caption">
              <Icon name="box" />{' '}{t("operations_with_a_clear_identity")}</span>
            {global ? (
              <SelectField
                label={t("company_scope")}
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                options={refs.data?.companies || []}
                placeholder={t("all_companies")}
                disabled={refs.loading}
              />
            ) : (
              <span className="mono">{t("access_limited_to_your_company")}</span>
            )}
          </div>
          {companyName.startsWith('DEMO ·') && (
            <p className="demo-banner">{t("controlled_demonstration_data_these_records_do_not_represent")}</p>
          )}
          <main id="app-contenido" tabIndex="-1" ref={content} className="app-content">
            <Outlet key={selected} />
          </main>
          <footer className="app-footer">
            <span>{t("logistech_2_0_control_sheet")}</span>
            <span>{t("tecsup_academic_project")}</span>
          </footer>
        </div>
      </div>
    </Tenant.Provider>
  )
}
