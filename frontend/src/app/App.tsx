import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './router/ProtectedRoute'
import { QueryProvider } from './providers/QueryProvider'
import { LoginPage } from '@/pages/login-page'
import { MainPage } from '@/pages/main-page'
import { ProfilePage } from '@/pages/profile-page'
import { RegisterPage } from '@/pages/register-page'
import { RecipesListPage } from '@/pages/recipes-list-page'
import { RecipePage } from '@/pages/recipe-page'
import { RecipeCreatePage } from '@/pages/recipe-create-page'
import { RecipeEditPage } from '@/pages/recipe-edit-page'

export function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/recipes" element={<RecipesListPage />} />
          <Route path="/recipes/:recipeId" element={<RecipePage />} />
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
          <Route
            path="/recipes/new"
            element={
              <ProtectedRoute>
                <RecipeCreatePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recipes/:recipeId/edit"
            element={
              <ProtectedRoute>
                <RecipeEditPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryProvider>
  )
}
