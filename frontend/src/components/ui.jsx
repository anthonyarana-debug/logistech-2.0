import { useEffect, useId, useRef, useState } from 'react'
import { Link } from 'react-router-dom'

const icons = {
  arrow: (
    <>
      <path d="M4 12h15M13 5l7 7-7 7" />
    </>
  ),
  box: (
    <>
      <path d="m12 3 9 5-9 5-9-5 9-5ZM3 8v9l9 5 9-5V8M12 13v9M7.5 5.5l9 5" />
    </>
  ),
  grid: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </>
  ),
  tag: <path d="M3 3h8l10 10-8 8L3 11V3Zm5 5h.01" />,
  search: (
    <>
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="m16 16 5 5" />
    </>
  ),
  menu: <path d="M4 6h16M4 12h16M4 18h16" />,
  close: <path d="m6 6 12 12M6 18 18 6" />,
  logout: (
    <>
      <path d="M10 4H4v16h6M10 12h11m-4-4 4 4-4 4" />
    </>
  ),
  plus: <path d="M12 4v16M4 12h16" />,
  edit: (
    <>
      <path d="m14 5 5 5M4 20l1-6L17 2l5 5L10 19l-6 1Z" />
    </>
  ),
  eye: (
    <>
      <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
    </>
  ),
  check: <path d="m5 12 4 4L20 5" />,
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 6v6l4 2" />
    </>
  ),
  warning: (
    <>
      <path d="m12 3 10 18H2L12 3ZM12 9v5M12 17h.01" />
    </>
  ),
}
export function Icon({ name, ...props }) {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {icons[name] || icons.box}
    </svg>
  )
}
export function Logo({ compact = false }) {
  return (
    <span className="brand">
      <svg viewBox="0 0 32 32" width="30" height="30" fill="none" aria-hidden="true">
        <path d="M4 13V4h9M28 19v9h-9M10 22l12-12" stroke="currentColor" strokeWidth="3" />
      </svg>
      <span>LogisTech{!compact && <sup>2.0</sup>}</span>
    </span>
  )
}
export function Button({
  children,
  variant = 'primary',
  busy = false,
  disabled = false,
  className = '',
  ...props
}) {
  return (
    <button
      className={`button button-${variant} ${className}`}
      disabled={busy || disabled}
      aria-busy={busy || undefined}
      {...props}
    >
      {busy ? <span className="spinner" aria-hidden="true" /> : null}
      {children}
    </button>
  )
}
export function FormField({ label, error, hint, children, ...props }) {
  const generated = useId(),
    id = props.id || generated
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {children ? (
        children(id)
      ) : (
        <input
          {...props}
          id={id}
          aria-invalid={!!error}
          aria-describedby={error || hint ? `${id}-help` : undefined}
        />
      )}{' '}
      {(error || hint) && (
        <p id={`${id}-help`} className={error ? 'field-error' : 'field-hint'}>
          {error || hint}
        </p>
      )}
    </div>
  )
}
export function SelectField({ label, options, placeholder = 'Seleccionar…', hint, ...props }) {
  return (
    <FormField label={label} hint={hint}>
      {(id) => (
        <select id={id} aria-describedby={hint ? `${id}-help` : undefined} {...props}>
          <option value="">{placeholder}</option>
          {options.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>
      )}
    </FormField>
  )
}
export function PasswordField({ label = 'Contraseña', hint, ...props }) {
  const [visible, setVisible] = useState(false)
  return (
    <FormField label={label} hint={hint}>
      {(id) => (
        <div className="password-input">
          <input
            {...props}
            id={id}
            aria-describedby={hint ? `${id}-help` : undefined}
            type={visible ? 'text' : 'password'}
          />
          <button
            type="button"
            aria-label={
              visible ? `Ocultar ${label.toLowerCase()}` : `Mostrar ${label.toLowerCase()}`
            }
            aria-pressed={visible}
            onClick={() => setVisible(!visible)}
          >
            <Icon name="eye" />
          </button>
        </div>
      )}
    </FormField>
  )
}
export function LoadingState({ label = 'Cargando información…' }) {
  return (
    <div className="loading-state" role="status">
      <span className="spinner" />
      {label}
    </div>
  )
}
export function EmptyState({ title = 'Todavía no hay registros', children, action }) {
  return (
    <section className="empty-state">
      <span className="empty-mark">
        <Icon name="box" />
      </span>
      <h2>{title}</h2>
      <p>{children}</p>
      {action}
    </section>
  )
}
export function ErrorState({ error, onRetry, title }) {
  const focus = useRef(null)
  useEffect(() => {
    focus.current?.focus()
  }, [error])
  return (
    <div className="error-state" role="alert" tabIndex="-1" ref={focus}>
      <Icon name="warning" />
      <div>
        <h2>
          {title ||
            (error?.status === 403 ? 'Acceso denegado' : 'No se pudo completar la operación')}
        </h2>
        <p>
          {error?.message || 'El servicio no está disponible. Intenta nuevamente.'}
          {error?.retryAfter ? ` Puedes reintentar en ${error.retryAfter} segundos.` : ''}
        </p>
        {onRetry && (
          <Button variant="secondary" onClick={onRetry}>
            Volver a intentar
          </Button>
        )}
      </div>
    </div>
  )
}
export function StatusBadge({ value }) {
  const names = {
    REGISTERED: 'Registrada',
    RECEIVED: 'Recibida',
    REJECTED: 'Rechazada',
    LOW: 'Baja',
    NORMAL: 'Normal',
    HIGH: 'Alta',
  }
  return <span className={`badge badge-${value?.toLowerCase()}`}>{names[value] || value}</span>
}
export function SearchBar({ value, onChange, placeholder = 'Buscar…', label = 'Buscar' }) {
  return (
    <label className="search-bar">
      <Icon name="search" />
      <span className="sr-only">{label}</span>
      <input
        type="search"
        value={value}
        maxLength={100}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
      />
    </label>
  )
}
export function FilterBar({ children, onClear }) {
  return (
    <div className="filter-bar">
      {children}
      {onClear && (
        <Button variant="text" onClick={onClear}>
          Limpiar filtros
        </Button>
      )}
    </div>
  )
}
export function DataTable({ caption, columns, rows }) {
  return (
    <div className="table-region" role="region" aria-label={caption} tabIndex="0">
      <table>
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr>
            {columns.map((col) => (
              <th scope="col" key={col.key}>
                {col.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              {columns.map((col) => (
                <td key={col.key}>{col.render ? col.render(row) : row[col.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
export function Modal({ title, children, onClose, busy = false, className = '' }) {
  const ref = useRef(null),
    titleId = useId()
  useEffect(() => {
    const el = ref.current
    el.showModal()
    return () => el.close()
  }, [])
  return (
    <dialog
      ref={ref}
      className={`modal ${className}`}
      aria-labelledby={titleId}
      onCancel={(event) => {
        event.preventDefault()
        if (!busy) onClose()
      }}
    >
      <header>
        <h2 id={titleId}>{title}</h2>
        <button
          type="button"
          className="icon-button"
          aria-label="Cerrar diálogo"
          disabled={busy}
          onClick={onClose}
        >
          <Icon name="close" />
        </button>
      </header>
      {children}
    </dialog>
  )
}
export function ConfirmModal({ title, children, onConfirm, onClose, busy, error }) {
  return (
    <Modal title={title} onClose={onClose} busy={busy}>
      <div className="modal-body">
        <p>{children}</p>
        {error && <ErrorState error={error} />}
      </div>
      <footer>
        <Button variant="secondary" onClick={onClose} disabled={busy}>
          Cancelar
        </Button>
        <Button variant="danger" onClick={onConfirm} busy={busy}>
          Eliminar definitivamente
        </Button>
      </footer>
    </Modal>
  )
}
export function Toast({ message, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 5500)
    return () => clearTimeout(timer)
  }, [onClose])
  return (
    <div className="toast" role="status">
      <Icon name="check" />
      {message}
      <button className="icon-button" onClick={onClose} aria-label="Cerrar notificación">
        <Icon name="close" />
      </button>
    </div>
  )
}
export function PageIntro({ eyebrow, title, children, action }) {
  return (
    <header className="page-intro">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {children && <p className="intro-description">{children}</p>}
      </div>
      {action}
    </header>
  )
}
export function PublicHeader() {
  return (
    <header className="public-header">
      <Link to="/" aria-label="LogisTech, inicio">
        <Logo />
      </Link>
      <nav aria-label="Navegación principal">
        <Link className="desktop-link" to="/#producto">
          Producto
        </Link>
        <Link to="/login">Acceder</Link>
        <Link className="button button-dark" to="/registro">
          Crear cuenta <Icon name="arrow" />
        </Link>
      </nav>
    </header>
  )
}
