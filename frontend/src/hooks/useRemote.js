import { useCallback, useEffect, useState } from 'react'
import { api } from '../services/api.js'

export function useRemote(path, query = {}, enabled = true) {
  const params = new URLSearchParams(
    Object.entries(query).filter(
      ([, value]) => value !== '' && value !== undefined && value !== null,
    ),
  ).toString()
  const key = path + (params ? `?${params}` : '')
  const [result, setResult] = useState({ key: '', data: null, loading: true, error: null })
  const [version, setVersion] = useState(0)
  const reload = useCallback(() => setVersion((n) => n + 1), [])
  useEffect(() => {
    if (!enabled) return
    const controller = new AbortController()
    let live = true
    setResult({ key, data: null, loading: true, error: null })
    api(key, { signal: controller.signal })
      .then((data) => {
        if (live) setResult({ key, data, loading: false, error: null })
      })
      .catch((error) => {
        if (live && error.name !== 'AbortError')
          setResult({ key, data: null, loading: false, error })
      })
    return () => {
      live = false
      controller.abort()
    }
  }, [key, version, enabled])
  return {
    ...(result.key === key && enabled ? result : { data: null, loading: enabled, error: null }),
    reload,
  }
}
export function useDebounced(value, delay = 300) {
  const [current, setCurrent] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setCurrent(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return current
}

export function useCollection(path, query = {}, enabled = true) {
  const scope = JSON.stringify([path, query])
  const [selection, setSelection] = useState({ scope: '', page: 1 })
  const page = selection.scope === scope ? selection.page : 1
  const remote = useRemote(path, { ...query, page }, enabled)
  const setPage = (next) => setSelection({ scope, page: next })
  useEffect(() => {
    setSelection((current) => current.scope === scope ? current : { scope, page: 1 })
  }, [scope])
  // A deletion can empty the last page. Keep the filters and return to the first page.
  useEffect(() => {
    if (remote.error?.status === 404 && page > 1)
      setSelection({ scope, page: 1 })
  }, [remote.error, page, scope])
  return {
    ...remote,
    data: remote.data?.results ?? null,
    count: remote.data?.count ?? 0,
    page,
    previous: Boolean(remote.data?.previous),
    next: Boolean(remote.data?.next),
    setPage,
  }
}
