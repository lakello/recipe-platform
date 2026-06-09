import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { useLogout } from '@/features/auth/hooks/useAuth'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { usePublicProfile } from '@/features/profile/hooks/usePublicProfile'
import { useUpdateProfile } from '@/features/profile/hooks/useUpdateProfile'
import { useRecipesList } from '@/features/recipes/hooks/useRecipes'
import { PhotoUpload } from '@/features/uploads/ui/PhotoUpload'
import { useAvatarUpload } from '@/features/uploads/hooks/useUpload'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

const schema = z.object({
  username: z
    .string()
    .min(3, 'Минимум 3 символа')
    .max(50, 'Максимум 50 символов'),
})

type FormData = z.infer<typeof schema>

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Лёгкий',
  medium: 'Средний',
  hard: 'Сложный',
}

export function ProfilePage() {
  const navigate = useNavigate()
  const { data: user } = useCurrentUser()
  const { data: publicProfile } = usePublicProfile(user?.id ?? '')
  const { mutate: logout, isPending: isLoggingOut } = useLogout()
  const { mutate: update, isPending: isUpdating, error, isSuccess } = useUpdateProfile()
  const { data: recipes } = useRecipesList()
  const { upload: uploadAvatar, isPending: isAvatarLoading, error: avatarError } = useAvatarUpload()

  const myRecipes = recipes?.filter((r) => r.author_id === user?.id && r.status !== 'deleted')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  useEffect(() => {
    if (user) reset({ username: user.username })
  }, [user, reset])

  if (!user) return null

  return (
    <div className="mx-auto max-w-lg px-4 py-12">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Button variant="secondary" onClick={() => navigate(-1)}>← Назад</Button>
          <Link to="/">
            <Button variant="secondary">На главную</Button>
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Профиль</h1>
        </div>
        <Button variant="secondary" loading={isLoggingOut} onClick={() => logout()}>
          Выйти
        </Button>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm mb-6">
        <div className="flex items-center gap-4 mb-6">
          <PhotoUpload
            currentUrl={user.avatar_url ?? undefined}
            onUpload={uploadAvatar}
            isPending={isAvatarLoading}
            error={avatarError}
            label="Загрузить аватар"
            shape="circle"
          />
          <div>
            <p className="font-semibold text-gray-900">{user.username}</p>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>
        <div className="flex gap-6 mb-6 pb-4 border-b border-gray-100">
          <div className="flex flex-col items-center">
            <span className="text-lg font-bold text-gray-900">
              {myRecipes?.length ?? 0}
            </span>
            <span className="text-xs text-gray-500">рецептов</span>
          </div>
          <Link
            to={`/users/${user.id}/followers`}
            className="flex flex-col items-center hover:opacity-75 transition-opacity"
          >
            <span className="text-lg font-bold text-gray-900">
              {publicProfile?.followers_count ?? 0}
            </span>
            <span className="text-xs text-gray-500">подписчиков</span>
          </Link>
          <Link
            to={`/users/${user.id}/following`}
            className="flex flex-col items-center hover:opacity-75 transition-opacity"
          >
            <span className="text-lg font-bold text-gray-900">
              {publicProfile?.following_count ?? 0}
            </span>
            <span className="text-xs text-gray-500">подписок</span>
          </Link>
        </div>

        <dl className="mb-6 space-y-3 text-sm">
          <div className="flex gap-2">
            <dt className="font-medium text-gray-500 w-20">Email:</dt>
            <dd className="text-gray-900">{user.email}</dd>
          </div>
          <div className="flex gap-2">
            <dt className="font-medium text-gray-500 w-20">Аккаунт:</dt>
            <dd className={user.is_active ? 'text-green-600' : 'text-red-500'}>
              {user.is_active ? 'Активен' : 'Заблокирован'}
            </dd>
          </div>
        </dl>

        <form
          onSubmit={handleSubmit((data) => update(data))}
          className="flex flex-col gap-4"
        >
          <Input
            label="Имя пользователя"
            error={errors.username?.message}
            {...register('username')}
          />
          {error && <p className="text-sm text-red-500">{error.message}</p>}
          {isSuccess && (
            <p className="text-sm text-green-600">Профиль обновлён</p>
          )}
          <Button type="submit" loading={isUpdating} disabled={!isDirty}>
            Сохранить
          </Button>
        </form>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Мои рецепты</h2>
          <Link to="/recipes/new">
            <Button>+ Создать рецепт</Button>
          </Link>
        </div>
        {!myRecipes && <p className="text-gray-500 text-sm">Загрузка...</p>}
        {myRecipes && myRecipes.length === 0 && (
          <p className="text-gray-500 text-sm">Рецептов пока нет.</p>
        )}
        <ul className="flex flex-col gap-3">
          {myRecipes?.map((recipe) => (
            <li key={recipe.id}>
              <Link
                to={`/recipes/${recipe.id}`}
                className="flex items-center justify-between gap-3 rounded-lg border border-gray-100 px-4 py-3 hover:bg-gray-50 transition-colors"
              >
                <div className="min-w-0">
                  <p className="font-medium text-gray-900 truncate">{recipe.title}</p>
                  {recipe.difficulty && (
                    <p className="text-xs text-gray-400 mt-0.5">
                      {DIFFICULTY_LABELS[recipe.difficulty]}
                      {recipe.cooking_time_minutes && ` · ${recipe.cooking_time_minutes} мин`}
                    </p>
                  )}
                </div>
                <div className="flex gap-1.5 shrink-0">
                  {recipe.status === 'draft' && (
                    <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
                      Черновик
                    </span>
                  )}
                  {recipe.visibility === 'private' && (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                      Приватный
                    </span>
                  )}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
