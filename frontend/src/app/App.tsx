import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './router/ProtectedRoute'
import { QueryProvider } from './providers/QueryProvider'
import { LoginPage } from '@/pages/login-page'
import { ProfilePage } from '@/pages/profile-page'
import { RegisterPage } from '@/pages/register-page'
import { RecipesListPage } from '@/pages/recipes-list-page'
import { RecipePage } from '@/pages/recipe-page'
import { RecipeCreatePage } from '@/pages/recipe-create-page'
import { RecipeEditPage } from '@/pages/recipe-edit-page'
import { DraftsPage } from '@/pages/drafts-page'
import { FavoritesPage } from '@/pages/favorites-page'
import { AdminCategoriesPage } from '@/pages/admin-categories-page'
import { PublicProfilePage } from '@/pages/user-profile-page'
import { FollowersPage } from '@/pages/followers-page'
import { FollowingPage } from '@/pages/following-page'
import { FeedPage } from '@/pages/feed-page'
import { SearchPage } from '@/pages/search-page'
import { MealPlanPage } from '@/pages/meal-plan-page'
import { ShoppingListPage } from '@/pages/shopping-list-page'

export function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/recipes" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/recipes" element={<RecipesListPage />} />
          <Route path="/recipes/:recipeId" element={<RecipePage />} />
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
          <Route
            path="/recipes/drafts"
            element={
              <ProtectedRoute>
                <DraftsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/favorites"
            element={
              <ProtectedRoute>
                <FavoritesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/categories"
            element={
              <ProtectedRoute>
                <AdminCategoriesPage />
              </ProtectedRoute>
            }
          />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/users/:userId" element={<PublicProfilePage />} />
          <Route path="/users/:userId/followers" element={<FollowersPage />} />
          <Route path="/users/:userId/following" element={<FollowingPage />} />
          <Route
            path="/meal-plan"
            element={
              <ProtectedRoute>
                <MealPlanPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/feed"
            element={
              <ProtectedRoute>
                <FeedPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/shopping-list"
            element={
              <ProtectedRoute>
                <ShoppingListPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryProvider>
  )
}
