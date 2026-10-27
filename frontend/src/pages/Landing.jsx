import { Link } from 'react-router-dom'
import { Icon, Logo, PublicHeader } from '../components/ui.jsx'

function ParcelDrawing() {
  return (
    <svg
      className="parcel-drawing"
      viewBox="0 0 560 470"
      fill="none"
      role="img"
      aria-label="Ilustración original de una caja con identificación propia y QR independiente; esquema conceptual"
    >
      <defs>
        <pattern id="guides" width="36" height="36" patternUnits="userSpaceOnUse">
          <path d="M36 0H0V36" stroke="#41574d" strokeWidth=".5" />
        </pattern>
      </defs>
      <rect width="560" height="470" fill="url(#guides)" />
      <path d="M60 395H500M90 55V430" stroke="#81978b" strokeDasharray="3 6" />
      <path
        d="m135 158 176-85 149 92-172 89-153-96Z"
        fill="#dce4d2"
        stroke="#101F20"
        strokeWidth="2"
      />
      <path d="M135 158v176l153 96V254l-153-96Z" fill="#aabe9d" stroke="#101F20" strokeWidth="2" />
      <path d="M288 254v176l172-92V165l-172 89Z" fill="#c5f278" stroke="#101F20" strokeWidth="2" />
      <path d="m210 122 151 96v84l31-17v-82l-151-97-31 16Z" fill="#203934" />
      <path d="m318 285 109-58v76l-109 58v-76Z" fill="#F4F6F2" stroke="#101F20" strokeWidth="1.5" />
      <path d="m332 285 81-43M332 300l49-26M332 319l81-43" stroke="#101F20" strokeWidth="3" />
      <path d="M43 86V61h25M500 383v26h-26" stroke="#C5F278" strokeWidth="3" />
      <text x="42" y="39" fill="#C5F278" fontSize="12" fontFamily="monospace" letterSpacing="2">
        SISTEMA DE IDENTIFICACIÓN
      </text>
      <text x="42" y="452" fill="#dce4d2" fontSize="12" fontFamily="monospace">
        CJ / IDENTIDAD PROPIA · QR INDEPENDIENTE
      </text>
    </svg>
  )
}

export default function Landing() {
  return (
    <div className="landing">
      <a className="skip-link" href="#contenido">
        Saltar al contenido
      </a>
      <PublicHeader />
      <main id="contenido" tabIndex="-1">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">
              <span className="status-dot" /> LOGÍSTICA CON IDENTIDAD PROPIA
            </p>
            <h1>
              Cada caja.
              <br />
              En su lugar.
              <br />
              <em>Bajo control.</em>
            </h1>
            <p className="hero-description">
              Deja de buscar entre datos dispersos. Identifica, organiza y consulta tu mercancía
              desde un solo espacio de trabajo.
            </p>
            <div className="hero-actions">
              <Link className="button button-dark" to="/registro">
                Comenzar con LogisTech <Icon name="arrow" />
              </Link>
              <Link className="text-link" to="/login">
                Ya tengo una cuenta <span aria-hidden="true">↗</span>
              </Link>
            </div>
            <p className="hero-note">
              Acceso por roles · Datos por empresa · Identificación alternativa
            </p>
          </div>
          <div className="hero-visual">
            <div className="visual-label">
              <span>LOGISTECH / OPERACIONES</span>
              <span>WEB 2.0</span>
            </div>
            <ParcelDrawing />
            <div className="visual-footer">
              <span className="status-dot" />
              <span>El control empieza por saber qué tienes.</span>
            </div>
          </div>
        </section>
        <section className="product-band" id="producto">
          <p className="eyebrow">MENOS FRICCIÓN. MÁS CLARIDAD.</p>
          <h2>
            Una hoja de control.
            <br />
            Todo el contexto que necesitas.
          </h2>
          <p>
            Categorías claras, cajas identificables y acceso limitado a quien corresponde. Una base
            funcional para el trabajo de almacén.
          </p>
        </section>
        <section className="process" aria-label="Proceso disponible">
          <div className="section-heading">
            <p className="eyebrow">DEL REGISTRO A LA CONSULTA</p>
            <h2>Orden en cada paso.</h2>
          </div>
          <div className="process-grid">
            {[
              [
                '01',
                'Clasifica con criterio.',
                'Organiza categorías y distingue mercancía frágil y perecedera. Ambas condiciones pueden coexistir.',
              ],
              [
                '02',
                'Dale una identidad.',
                'Registra cada caja con un identificador interno propio, independiente de su código QR.',
              ],
              [
                '03',
                'Encuentra el contexto.',
                'Busca, filtra y consulta producto, cantidad, sucursal, prioridad y estado dentro de tu empresa.',
              ],
            ].map(([n, title, copy]) => (
              <article key={n}>
                <span className="step-number">{n}</span>
                <h3>{title}</h3>
                <p>{copy}</p>
                <Icon name="arrow" />
              </article>
            ))}
          </div>
        </section>
        <section className="capabilities">
          <div>
            <p className="eyebrow">LO QUE PUEDES HACER HOY</p>
            <h2>
              Herramientas concretas.
              <br />
              Permisos claros.
            </h2>
            <p>
              El operador trabaja con sus cajas. El administrador organiza los recursos de su
              empresa. La autorización se verifica en el servidor.
            </p>
            <Link className="text-link" to="/login">
              Entrar al espacio de trabajo <Icon name="arrow" />
            </Link>
          </div>
          <ul>
            {[
              'Registro e inicio de sesión seguros',
              'Categorías con fragilidad y perecibilidad',
              'Cajas con búsqueda manual e identificadores propios',
              'Acciones disponibles según el rol y el estado',
            ].map((text) => (
              <li key={text}>
                <Icon name="check" />
                {text}
              </li>
            ))}
          </ul>
        </section>
        <section className="future-note">
          <span className="badge">EN EL CAMINO</span>
          <p>
            Cámara y escaneo QR, recepciones avanzadas, historial y reportes forman parte de futuras
            fases. La consulta manual y los CRUD iniciales ya están disponibles.
          </p>
        </section>
        <section className="closing-cta">
          <div>
            <p className="eyebrow">EL SIGUIENTE PASO ES SIMPLE</p>
            <h2>
              Empieza a poner
              <br />
              las cosas en orden.
            </h2>
          </div>
          <Link className="button button-primary" to="/registro">
            Crear mi cuenta <Icon name="arrow" />
          </Link>
        </section>
      </main>
      <footer className="public-footer">
        <Logo compact />
        <p>
          Proyecto académico · TECSUP
          <br />
          <span>Desarrollo de Soluciones en la Nube</span>
        </p>
        <Link to="/estado">
          Estado del servicio <Icon name="arrow" />
        </Link>
      </footer>
    </div>
  )
}
