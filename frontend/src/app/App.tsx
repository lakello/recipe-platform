import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './router/ProtectedRoute'
import { QueryProvider } from './providers/QueryProvider'
import { LoginPage } from '@/pages/login-page'
import { MainPage } from '@/pages/main-page'
import { ProfilePage } from '@/pages/profile-page'
import { RegisterPage } from '@/pages/register-page'

export function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryProvider>
  )
}
