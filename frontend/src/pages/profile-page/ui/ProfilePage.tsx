import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { useLogout } from '@/features/auth/hooks/useAuth'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'
import { useUpdateProfile } from '@/features/profile/hooks/useUpdateProfile'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

const schema = z.object({
  username: z
    .string()
    .min(3, 'Минимум 3 символа')
    .max(50, 'Максимум 50 символов'),
})

type FormData = z.infer<typeof schema>

export function ProfilePage() {
  const { data: user } = useCurrentUser()
  const { mutate: logout, isPending: isLoggingOut } = useLogout()
  const { mutate: update, isPending: isUpdating, error, isSuccess } = useUpdateProfile()

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
        <h1 className="text-2xl font-bold text-gray-900">Профиль</h1>
        <Button variant="secondary" loading={isLoggingOut} onClick={() => logout()}>
          Выйти
        </Button>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm">
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
          <Button
            type="submit"
            loading={isUpdating}
            disabled={!isDirty}
          >
            Сохранить
          </Button>
        </form>
      </div>
    </div>
  )
}
