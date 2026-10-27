import { createContext, useContext, useEffect, useRef, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth.jsx'
import { useRemote } from '../hooks/useRemote.js'
import { Button, Icon, Logo, SelectField } from './ui.jsx'

const Tenant = createContext(null)
export const useTenant = () => useContext(Tenant)
export const roleNames = {
  SUPERADMIN: 'Superadministrador',
  COMPANY_ADMIN: 'Administrador de empresa',
  OPERATOR: 'Operador',
}
const navigation = [
  ['/app', 'grid', 'Vista general'],
  ['/app/cajas', 'box', 'Cajas'],
  ['/app/categorias', 'tag', 'Categorías'],
]
export default function AppShell() {
  const auth = useAuth(),
    location = useLocation()
  const [company, setCompany] = useState(''),
    [menu, setMenu] = useState(false)
  const dialog = useRef(null),
    content = useRef(null)
  const global = auth.user.role === 'SUPERADMIN'
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
    (global ? 'Todas las empresas' : auth.user.company.name)
  function sidebar(mobile = false) {
    return (
      <>
        <Link className="sidebar-brand" to="/app" aria-label="LogisTech, vista general">
          <Logo compact />
        </Link>
        <p className="sidebar-section">ESPACIO DE TRABAJO</p>
        <nav aria-label={mobile ? 'Navegación móvil' : 'Navegación del sistema'}>
          {navigation.map(([to, icon, text]) => (
            <NavLink key={to} to={to} end={to === '/app'} onClick={() => setMenu(false)}>
              <Icon name={icon} />
              {text}
              <span className="nav-active-mark" />
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-upcoming">
          <p className="sidebar-section">PRÓXIMAMENTE</p>
          <Link to="/app/en-desarrollo" onClick={() => setMenu(false)}>
            <Icon name="clock" />
            Recepciones<span className="soon-label">F6</span>
          </Link>
        </div>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <p>
            Un lugar para cada cosa.
            <br />
            <strong>Contexto para cada decisión.</strong>
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
        <a className="skip-link" href="#app-contenido">
          Saltar al contenido
        </a>
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
            aria-label="Cerrar menú"
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
              aria-label="Abrir menú"
              onClick={() => setMenu(true)}
            >
              <Icon name="menu" />
            </button>
            <div className="header-context">
              <span className="mono eyebrow">EMPRESA / CONTEXTO</span>
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
                aria-label="Cerrar sesión"
              >
                <Icon name="logout" />
              </button>
            </div>
          </header>
          <div className="context-bar">
            <span className="context-caption">
              <Icon name="box" /> Operaciones con identidad propia
            </span>
            {global ? (
              <SelectField
                label="Ámbito empresarial"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                options={refs.data?.companies || []}
                placeholder="Todas las empresas"
                disabled={refs.loading}
              />
            ) : (
              <span className="mono">ACCESO LIMITADO A TU EMPRESA</span>
            )}
          </div>
          {companyName.startsWith('DEMO ·') && (
            <p className="demo-banner">
              Datos de demostración controlados. No representan operaciones de producción.
            </p>
          )}
          <main id="app-contenido" tabIndex="-1" ref={content} className="app-content">
            <Outlet />
          </main>
          <footer className="app-footer">
            <span>LogisTech 2.0 / Hoja de control</span>
            <span>TECSUP · Proyecto académico</span>
          </footer>
        </div>
      </div>
    </Tenant.Provider>
  )
}
