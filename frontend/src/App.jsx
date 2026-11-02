import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { LanguageProvider } from './context/LanguageContext'
import { FarmProvider } from './context/FarmProvider'
import LandingPage from './pages/landing/LandingPage'
import AppLayout from './components/layout/AppLayout'
import DashboardPage from './pages/app/DashboardPage'
import AnalyzePage from './pages/app/analyze/AnalyzePage'
import RecommendationPage from './pages/app/RecommendationPage'
import HistoryPage from './pages/app/HistoryPage'
import ProfilePage from './pages/app/ProfilePage'

export default function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          {/* Public marketing landing page */}
          <Route path="/" element={<LandingPage />} />

          {/* Authenticated app shell with sidebar — shares farm state via FarmProvider */}
          <Route
            path="/app"
            element={
              <FarmProvider>
                <AppLayout />
              </FarmProvider>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="analyze" element={<AnalyzePage />} />
            <Route path="recommendations/:id" element={<RecommendationPage />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  )
}
