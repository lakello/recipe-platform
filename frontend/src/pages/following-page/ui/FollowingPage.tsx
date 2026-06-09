import { useNavigate, useParams } from 'react-router-dom'
import { useFollowing } from '@/features/follows/hooks/useFollows'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { FollowButton } from '@/features/follows/ui/FollowButton'
import { UserLink } from '@/shared/ui/UserLink'
import { Button } from '@/shared/ui/Button'

export function FollowingPage() {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()
  const { data, isPending, error } = useFollowing(userId!)
  const { data: currentUser } = useCurrentUser()

  return (
    <div className="mx-auto max-w-lg px-4 py-12">
      <div className="mb-8">
        <Button variant="secondary" onClick={() => navigate(-1)}>← Назад</Button>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h1 className="text-lg font-semibold text-gray-900 mb-4">Подписки</h1>

        {isPending && <p className="text-gray-500 text-sm">Загрузка...</p>}
        {error && <p className="text-red-500 text-sm">{error.message}</p>}
        {data && data.items.length === 0 && (
          <p className="text-gray-500 text-sm">Нет подписок.</p>
        )}

        <ul className="flex flex-col divide-y divide-gray-100">
          {data?.items.map((u) => (
            <li key={u.id} className="flex items-center justify-between py-3">
              <UserLink userId={u.id} username={u.username} avatarUrl={u.avatar_url} size="md" />
              {currentUser && currentUser.id !== u.id && (
                <FollowButton userId={u.id} isFollowing={u.is_following} />
              )}
            </li>
          ))}
        </ul>

        {data && (
          <p className="text-xs text-gray-400 text-center mt-4">
            {data.total} подпис{data.total === 1 ? 'ка' : data.total < 5 ? 'ки' : 'ок'}
          </p>
        )}
      </div>
    </div>
  )
}
