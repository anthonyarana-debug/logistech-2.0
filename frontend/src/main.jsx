import { t, defaultLocale } from './i18n/index.js'
import { createRoot } from 'react-dom/client'
import { useEffect } from 'react'
import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom'
import { AuthProvider, Protected, SessionExpired } from './auth.jsx'
import AppShell from './components/AppShell.jsx'
import Landing from './pages/Landing.jsx'
import AuthPage from './pages/AuthPage.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Administration from './pages/Administration.jsx'
import Resources from './pages/Resources.jsx'
import BoxDetail from './pages/BoxDetail.jsx'
import { InDevelopment, NotFound, ServiceStatus } from './pages/Special.jsx'
import '@fontsource/ibm-plex-sans/latin-400.css'
import '@fontsource/ibm-plex-sans/latin-500.css'
import '@fontsource/ibm-plex-sans/latin-600.css'
import '@fontsource/ibm-plex-mono/latin-400.css'
import './styles/index.css'

function ScrollNavigation() {
  const location = useLocation()
  useEffect(() => {
    if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView()
    else if (!location.pathname.startsWith('/app')) globalThis.scrollTo(0, 0)
  }, [location.pathname, location.hash])
  return null
}

document.documentElement.lang = defaultLocale
document.title = t('page_title')
document.querySelector('meta[name="description"]').content = t('page_description')

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <ScrollNavigation />
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<AuthPage key="login" />} />
        <Route path="/registro" element={<AuthPage key="register" signup />} />
        <Route path="/403" element={<NotFound forbidden />} />
        <Route path="/sesion-expirada" element={<SessionExpired />} />
        <Route path="/estado" element={<ServiceStatus />} />
        <Route path="/servicio-no-disponible" element={<ServiceStatus />} />
        <Route
          path="/app"
          element={
            <Protected>
              <AppShell />
            </Protected>
          }
        >
          <Route index element={<Dashboard />} />
          {['companies', 'branches', 'products', 'users'].map(kind =>
            <Route key={kind} path={kind} element={<Administration key={kind} kind={kind} />} />)}
          <Route path="categorias" element={<Resources key="categories" kind="categories" />} />
          <Route path="cajas" element={<Resources key="boxes" kind="boxes" />} />
          <Route path="cajas/:id" element={<BoxDetail />} />
          <Route path="en-desarrollo" element={<InDevelopment />} />
          <Route path="*" element={<NotFound />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthProvider>
  </BrowserRouter>,
)
