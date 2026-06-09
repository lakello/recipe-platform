import { useState } from 'react'
import { AdminLayout } from '@/widgets/admin-layout'
import { useAdminUsers, useAssignRole, useBlockUser, useUnblockUser } from '@/features/admin/hooks/useAdmin'
import type { AdminUser } from '@/features/admin/api/adminApi'
import type { UserRole } from '@/features/profile/api/profileApi'
import { Button } from '@/shared/ui/Button'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'

const ROLES: UserRole[] = ['user', 'moderator', 'admin', 'superadmin']

function UserRow({ user, currentUserId }: { user: AdminUser; currentUserId?: string }) {
  const [showRoleSelect, setShowRoleSelect] = useState(false)
  const { mutate: assignRole, isPending: isAssigning } = useAssignRole()
  const { mutate: block, isPending: isBlocking } = useBlockUser()
  const { mutate: unblock, isPending: isUnblocking } = useUnblockUser()

  const isSelf = user.id === currentUserId

  return (
    <tr className="border-b border-gray-100 last:border-0">
      <td className="py-3 pr-4">
        <p className="font-medium text-gray-900">{user.username}</p>
        <p className="text-xs text-gray-400">{user.email}</p>
      </td>
      <td className="py-3 pr-4">
        {showRoleSelect ? (
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
              {ROLES.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
            <Button variant="secondary" onClick={() => setShowRoleSelect(false)}>
              ✕
            </Button>
          </div>
        ) : (
          <button
            onClick={() => setShowRoleSelect(true)}
            disabled={isSelf || isAssigning}
            className="text-sm px-2 py-0.5 rounded-full font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50"
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
        {!isSelf && (
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
  const { data, isPending, error } = useAdminUsers(page)
  const { data: currentUser } = useCurrentUser()

  return (
    <AdminLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Пользователи</h1>

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
                  <UserRow key={u.id} user={u} currentUserId={currentUser?.id} />
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
