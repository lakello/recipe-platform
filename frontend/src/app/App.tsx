import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './router/ProtectedRoute'
import { AdminRoute } from './router/AdminRoute'
import { QueryProvider } from './providers/QueryProvider'
import { NotificationBell } from '@/features/notifications/ui/NotificationBell'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'

const LoginPage = lazy(() => import('@/pages/login-page').then((m) => ({ default: m.LoginPage })))
const RegisterPage = lazy(() => import('@/pages/register-page').then((m) => ({ default: m.RegisterPage })))
const RecipesListPage = lazy(() => import('@/pages/recipes-list-page').then((m) => ({ default: m.RecipesListPage })))
const RecipePage = lazy(() => import('@/pages/recipe-page').then((m) => ({ default: m.RecipePage })))
const RecipeCreatePage = lazy(() => import('@/pages/recipe-create-page').then((m) => ({ default: m.RecipeCreatePage })))
const RecipeEditPage = lazy(() => import('@/pages/recipe-edit-page').then((m) => ({ default: m.RecipeEditPage })))
const DraftsPage = lazy(() => import('@/pages/drafts-page').then((m) => ({ default: m.DraftsPage })))
const FavoritesPage = lazy(() => import('@/pages/favorites-page').then((m) => ({ default: m.FavoritesPage })))
const ProfilePage = lazy(() => import('@/pages/profile-page').then((m) => ({ default: m.ProfilePage })))
const PublicProfilePage = lazy(() => import('@/pages/user-profile-page').then((m) => ({ default: m.PublicProfilePage })))
const FollowersPage = lazy(() => import('@/pages/followers-page').then((m) => ({ default: m.FollowersPage })))
const FollowingPage = lazy(() => import('@/pages/following-page').then((m) => ({ default: m.FollowingPage })))
const FeedPage = lazy(() => import('@/pages/feed-page').then((m) => ({ default: m.FeedPage })))
const SearchPage = lazy(() => import('@/pages/search-page').then((m) => ({ default: m.SearchPage })))
const MealPlanPage = lazy(() => import('@/pages/meal-plan-page').then((m) => ({ default: m.MealPlanPage })))
const ShoppingListPage = lazy(() => import('@/pages/shopping-list-page').then((m) => ({ default: m.ShoppingListPage })))
const NotificationsPage = lazy(() => import('@/pages/notifications-page').then((m) => ({ default: m.NotificationsPage })))
const AdminCategoriesPage = lazy(() => import('@/pages/admin-categories-page').then((m) => ({ default: m.AdminCategoriesPage })))
const AdminUsersPage = lazy(() => import('@/pages/admin-users-page').then((m) => ({ default: m.AdminUsersPage })))
const AdminRecipesPage = lazy(() => import('@/pages/admin-recipes-page').then((m) => ({ default: m.AdminRecipesPage })))
const AdminCommentsPage = lazy(() => import('@/pages/admin-comments-page').then((m) => ({ default: m.AdminCommentsPage })))
const AdminReportsPage = lazy(() => import('@/pages/admin-reports-page').then((m) => ({ default: m.AdminReportsPage })))

function GlobalBell() {
  const { data: user } = useCurrentUser()
  if (!user) return null
  return (
    <div className="fixed top-3 right-4 z-50">
      <NotificationBell />
    </div>
  )
}

export function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <GlobalBell />
        <Suspense
          fallback={
            <div className="grid min-h-screen place-items-center" role="status">
              Загрузка…
            </div>
          }
        >
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
              <AdminRoute minRole="admin">
                <AdminCategoriesPage />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <AdminRoute minRole="admin">
                <AdminUsersPage />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/recipes"
            element={
              <AdminRoute minRole="moderator">
                <AdminRecipesPage />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/comments"
            element={
              <AdminRoute minRole="moderator">
                <AdminCommentsPage />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/reports"
            element={
              <AdminRoute minRole="moderator">
                <AdminReportsPage />
              </AdminRoute>
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
          <Route
            path="/notifications"
            element={
              <ProtectedRoute>
                <NotificationsPage />
              </ProtectedRoute>
            }
          />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </QueryProvider>
  )
}
