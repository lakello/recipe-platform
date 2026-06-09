import { Link, useLocation } from 'react-router-dom'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'

const NAV_ITEMS = [
  { label: 'Пользователи', path: '/admin/users', minRole: 'admin' },
  { label: 'Рецепты', path: '/admin/recipes', minRole: 'moderator' },
  { label: 'Комментарии', path: '/admin/comments', minRole: 'moderator' },
  { label: 'Жалобы', path: '/admin/reports', minRole: 'moderator' },
  { label: 'Категории', path: '/admin/categories', minRole: 'admin' },
] as const

const ROLE_ORDER = ['user', 'moderator', 'admin', 'superadmin']

function hasAccess(userRole: string, minRole: string): boolean {
  return ROLE_ORDER.indexOf(userRole) >= ROLE_ORDER.indexOf(minRole)
}

interface Props {
  children: React.ReactNode
}

export function AdminLayout({ children }: Props) {
  const { data: user } = useCurrentUser()
  const { pathname } = useLocation()

  const visibleItems = NAV_ITEMS.filter(
    (item) => user && hasAccess(user.role, item.minRole),
  )

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-56 shrink-0 bg-white border-r border-gray-200 flex flex-col">
        <div className="px-4 py-5 border-b border-gray-200">
          <Link to="/recipes" className="text-sm text-gray-500 hover:text-gray-700">
            ← На сайт
          </Link>
          <p className="mt-2 font-bold text-gray-900">Панель управления</p>
          {user && (
            <p className="text-xs text-gray-400 mt-0.5">{user.role}</p>
          )}
        </div>
        <nav className="flex-1 py-4">
          <ul className="space-y-0.5 px-2">
            {visibleItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    pathname.startsWith(item.path)
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
      <main className="flex-1 p-8 overflow-auto">{children}</main>
    </div>
  )
}
