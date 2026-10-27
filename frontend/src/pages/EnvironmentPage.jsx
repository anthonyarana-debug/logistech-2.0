import { useEffect, useState } from 'react'
import { getHealth } from '../services/health.js'

export function EnvironmentPage() {
  const [state, setState] = useState({ status: 'loading' })

  async function check() {
    setState({ status: 'loading' })
    try {
      await getHealth()
      setState({ status: 'ready' })
    } catch {
      setState({ status: 'error' })
    }
  }

  useEffect(() => { check() }, [])

  const messages = {
    loading: ['Verificando conexión', 'Consultando la API y PostgreSQL…'],
    ready: ['Entorno conectado', 'La API respondió y confirmó una consulta a PostgreSQL.'],
    error: ['Servicio no disponible', 'No se pudo confirmar el estado. Comprueba los servicios locales y vuelve a intentar.'],
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8 sm:px-12">
      <header className="flex items-center justify-between border-b border-white/15 pb-6">
        <span className="text-xl font-semibold tracking-tight">logistech<span className="text-lime-300"> / 2.0</span></span>
        <span className="rounded-full border border-white/20 px-3 py-1 text-xs">Desarrollo local</span>
      </header>
      <section className="grid flex-1 items-center gap-12 py-16 md:grid-cols-[1.15fr_1fr]">
        <div>
          <p className="mb-5 text-xs font-semibold uppercase tracking-[0.2em] text-lime-300">Fase 01 · Infraestructura</p>
          <h1 className="max-w-lg text-4xl leading-tight font-semibold tracking-tight sm:text-6xl">Una base para conectar tu logística.</h1>
          <p className="mt-6 max-w-md leading-7 text-slate-300">Entorno inicial de LogisTech 2.0. Esta pantalla comprueba la conexión real entre la web, la API y la base de datos.</p>
          <p className="mt-5 text-sm text-slate-400">Registro, inventario y operaciones se incorporarán en las siguientes fases aprobadas.</p>
        </div>
        <div className="rounded-2xl border border-white/15 bg-white/5 p-7 sm:p-9">
          <p className="mb-8 text-xs uppercase tracking-widest text-slate-400">Estado del entorno</p>
          <div role="status" aria-live="polite" aria-atomic="true">
            <span aria-hidden="true" className={`mb-5 block h-3 w-3 rounded-full ${state.status === 'ready' ? 'bg-lime-300' : state.status === 'error' ? 'bg-orange-300' : 'animate-pulse bg-slate-300'}`} />
            <h2 className="text-2xl font-semibold">{messages[state.status][0]}</h2>
            <p className="mt-3 min-h-20 text-sm leading-6 text-slate-300">{messages[state.status][1]}</p>
          </div>
          <button type="button" onClick={check} disabled={state.status === 'loading'} className="mt-6 w-full rounded-lg bg-lime-300 px-5 py-3 text-sm font-semibold text-emerald-950 transition hover:bg-lime-200 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-lime-300 disabled:cursor-wait disabled:opacity-60">{state.status === 'loading' ? 'Comprobando…' : 'Volver a comprobar'}</button>
          <p className="mt-5 text-xs leading-5 text-slate-400">Sin datos de inventario simulados. Comprobación de disponibilidad, no de funcionalidad completa.</p>
        </div>
      </section>
      <footer className="border-t border-white/15 pt-5 text-xs text-slate-400">TECSUP · Desarrollo de Soluciones en la Nube</footer>
    </main>
  )
}
