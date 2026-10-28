import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button, ErrorState, FormField, PageIntro, StatusBadge } from '../components/ui.jsx'
import { t } from '../i18n/index.js'
import { resolveCode } from '../services/traceability.js'

export function CodeLookup({ onResolved }) {
  const [code, setCode] = useState(''), [busy, setBusy] = useState(false), [error, setError] = useState(null)
  async function submit(event) {
    event.preventDefault()
    onResolved(null)
    setBusy(true); setError(null)
    try { onResolved(await resolveCode(code)) } catch (error) { setError(error) } finally { setBusy(false) }
  }
  return <form onSubmit={submit} className="detail-panel">
    <FormField label={t('trace_code')} value={code} onChange={e => { setCode(e.target.value); onResolved(null) }} disabled={busy} required maxLength={100} hint={t('trace_code_hint')} />
    <Button variant="dark" busy={busy}>{t('trace_resolve')}</Button>
    {error && <ErrorState error={error} title={error.status === 404 ? t('box_unavailable') : undefined} />}
  </form>
}

function Camera({ onResolved }) {
  const video = useRef(null), stream = useRef(null), run = useRef(0), timer = useRef(null)
  const [active, setActive] = useState(false), [message, setMessage] = useState(''), [error, setError] = useState(null)
  function stop() {
    run.current++; clearTimeout(timer.current)
    stream.current?.getTracks().forEach(track => track.stop()); stream.current = null
    if (video.current) video.current.srcObject = null
    setActive(false)
  }
  useEffect(() => () => {
    run.current++; clearTimeout(timer.current)
    stream.current?.getTracks().forEach(track => track.stop())
  }, [])
  async function start() {
    onResolved(null)
    setError(null); setMessage('')
    if (!globalThis.isSecureContext || !globalThis.navigator.mediaDevices?.getUserMedia || !globalThis.BarcodeDetector) {
      setMessage(t('trace_camera_unavailable')); return
    }
    stop()
    const generation = run.current
    setActive(true)
    try {
      const detector = new globalThis.BarcodeDetector({ formats: ['qr_code'] })
      const acquired = await globalThis.navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
      if (generation !== run.current) { acquired.getTracks().forEach(track => track.stop()); return }
      stream.current = acquired; video.current.srcObject = acquired; await video.current.play()
      async function detect() {
        if (generation !== run.current) return
        try {
          const codes = await detector.detect(video.current)
          if (generation !== run.current) return
          if (codes.length) {
            stop()
            try { onResolved(await resolveCode(codes[0].rawValue)) } catch (error) { setError(error) }
            return
          }
          timer.current = setTimeout(detect, 350)
        } catch { stop(); setMessage(t('trace_camera_unavailable')) }
      }
      await detect()
    } catch {
      if (generation !== run.current) return
      stop(); setMessage(t('trace_camera_denied'))
    }
  }
  return <section className="detail-panel">
    <h2>{t('trace_camera')}</h2><p>{t('trace_camera_privacy')}</p>
    <video ref={video} muted playsInline hidden={!active} style={{ width: '100%', maxHeight: 320 }} aria-label={t('trace_camera_preview')} />
    <Button type="button" variant="secondary" onClick={active ? stop : start}>{t(active ? 'trace_stop_camera' : 'trace_start_camera')}</Button>
    {message && <p role="status">{message}</p>}{error && <ErrorState error={error} />}
  </section>
}

export default function Identification() {
  const [box, setBox] = useState(null)
  return <>
    <PageIntro eyebrow={t('identification')} title={t('trace_identify')}>{t('trace_identify_description')}</PageIntro>
    <div className="box-detail-grid"><CodeLookup onResolved={setBox} /><Camera onResolved={setBox} /></div>
    {box && <section className="record-actions" aria-live="polite"><div><h2>{box.internal_id}</h2><p>{box.product_name} · {box.branch_name}</p><StatusBadge value={box.status} /></div>
      <Link className="button button-dark" to={`/app/cajas/${box.id}`}>{t('box_details')}</Link></section>}
  </>
}
