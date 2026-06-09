import { useState } from 'react'
import { AdminLayout } from '@/widgets/admin-layout'
import { useAdminUsers, useAssignRole, useBlockUser, useUnblockUser } from '@/features/admin/hooks/useAdmin'
import type { AdminUser } from '@/features/admin/api/adminApi'
import type { UserRole } from '@/features/profile/api/profileApi'
import { Button } from '@/shared/ui/Button'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'

const ASSIGNABLE_ROLES: UserRole[] = ['user', 'moderator', 'admin']
const FILTER_ROLES = ['', 'user', 'moderator', 'admin', 'superadmin'] as const

function UserRow({
  user,
  currentUser,
}: {
  user: AdminUser
  currentUser?: { id: string; role: UserRole }
}) {
  const [showRoleSelect, setShowRoleSelect] = useState(false)
  const { mutate: assignRole, isPending: isAssigning } = useAssignRole()
  const { mutate: block, isPending: isBlocking } = useBlockUser()
  const { mutate: unblock, isPending: isUnblocking } = useUnblockUser()

  const isSelf = user.id === currentUser?.id
  const actorRole = currentUser?.role
  const targetIsSuperadmin = user.role === 'superadmin'

  // Who can block: only superadmin, and not another superadmin/self
  const canBlock = actorRole === 'superadmin' && !isSelf && !targetIsSuperadmin

  // Assignable roles based on actor
  const rolesForActor =
    actorRole === 'superadmin'
      ? ASSIGNABLE_ROLES
      : actorRole === 'admin'
        ? (['user', 'moderator'] as UserRole[])
        : []

  // Can change role: not self, not superadmin target, admin can't touch admin
  const canChangeRole =
    !isSelf &&
    !targetIsSuperadmin &&
    rolesForActor.length > 0 &&
    !(actorRole === 'admin' && user.role === 'admin')

  return (
    <tr className="border-b border-gray-100 last:border-0">
      <td className="py-3 pr-4">
        <p className="font-medium text-gray-900">{user.username}</p>
        <p className="text-xs text-gray-400">{user.email}</p>
      </td>
      <td className="py-3 pr-4">
        {showRoleSelect && canChangeRole ? (
          <div className="flex items-center gap-2">
            <select
              className="text-sm border border-gray-300 rounded-lg px-2 py-1"
              defaultValue={user.role}
              onChange={(e) => {
                assignRole(
                  { userId: user.id, role: e.target.value as UserRole },
                  { onSuccess: () => setShowRoleSelect(false) },
                )
              }}
            >
              {rolesForActor.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
            <Button variant="secondary" onClick={() => setShowRoleSelect(false)}>
              ✕
            </Button>
          </div>
        ) : (
          <button
            onClick={() => canChangeRole && setShowRoleSelect(true)}
            disabled={!canChangeRole || isAssigning}
            className="text-sm px-2 py-0.5 rounded-full font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-default"
          >
            {user.role}
          </button>
        )}
      </td>
      <td className="py-3 pr-4">
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            user.is_active
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
          }`}
        >
          {user.is_active ? 'активен' : 'заблокирован'}
        </span>
      </td>
      <td className="py-3 text-right">
        {canBlock && (
          user.is_active ? (
            <Button
              variant="danger"
              loading={isBlocking}
              onClick={() => {
                if (confirm(`Заблокировать пользователя ${user.username}?`)) {
                  block({ userId: user.id })
                }
              }}
            >
              Заблокировать
            </Button>
          ) : (
            <Button
              variant="secondary"
              loading={isUnblocking}
              onClick={() => unblock(user.id)}
            >
              Разблокировать
            </Button>
          )
        )}
      </td>
    </tr>
  )
}

export function AdminUsersPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const { data, isPending, error } = useAdminUsers(page, search || undefined, roleFilter || undefined)
  const { data: currentUser } = useCurrentUser()

  const handleSearch = (value: string) => {
    setSearch(value)
    setPage(1)
  }

  const handleRoleFilter = (value: string) => {
    setRoleFilter(value)
    setPage(1)
  }

  return (
    <AdminLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Пользователи</h1>

      <div className="flex gap-3 mb-4">
        <input
          type="text"
          placeholder="Поиск по имени или email..."
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1 max-w-xs"
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
        />
        <select
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
          value={roleFilter}
          onChange={(e) => handleRoleFilter(e.target.value)}
        >
          <option value="">Все роли</option>
          {FILTER_ROLES.filter(Boolean).map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
      </div>

      {isPending && <p className="text-gray-500">Загрузка...</p>}
      {error && <p className="text-red-500">{error.message}</p>}

      {data && (
        <>
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="px-4 py-3">Пользователь</th>
                  <th className="px-4 py-3">Роль</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="px-4">
                {data.items.map((u) => (
                  <UserRow key={u.id} user={u} currentUser={currentUser} />
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-gray-500">
              Всего: {data.total}
            </p>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p - 1)}
                disabled={page === 1}
              >
                ←
              </Button>
              <span className="text-sm text-gray-600 self-center">стр. {page}</span>
              <Button
                variant="secondary"
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.has_more}
              >
                →
              </Button>
            </div>
          </div>
        </>
      )}
    </AdminLayout>
  )
}
