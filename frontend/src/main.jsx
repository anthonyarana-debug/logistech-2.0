import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import { EnvironmentPage } from './pages/EnvironmentPage.jsx'
import './styles/index.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<EnvironmentPage />} />
        <Route path="*" element={
          <main className="mx-auto max-w-xl p-10">
            <h1 className="text-3xl font-semibold">Ruta no disponible</h1>
            <p className="my-4">Este entorno contiene únicamente la configuración de la Fase 1.</p>
            <Link className="underline" to="/">Volver al estado del entorno</Link>
          </main>
        } />
      </Routes>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)
