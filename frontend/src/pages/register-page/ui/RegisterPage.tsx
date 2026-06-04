import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'
import { useRegister } from '@/features/auth/hooks/useAuth'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

const schema = z.object({
  email: z.string().email('Некорректный email'),
  username: z
    .string()
    .min(3, 'Минимум 3 символа')
    .max(50, 'Максимум 50 символов'),
  password: z.string().min(8, 'Минимум 8 символов'),
})

type FormData = z.infer<typeof schema>

export function RegisterPage() {
  const { mutate: register, isPending, error } = useRegister()
  const {
    register: formRegister,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-sm rounded-xl bg-white p-8 shadow-sm">
        <h1 className="mb-6 text-2xl font-bold text-gray-900">Регистрация</h1>
        <form
          onSubmit={handleSubmit((data) => register(data))}
          className="flex flex-col gap-4"
        >
          <Input
            label="Email"
            type="email"
            error={errors.email?.message}
            {...formRegister('email')}
          />
          <Input
            label="Имя пользователя"
            error={errors.username?.message}
            {...formRegister('username')}
          />
          <Input
            label="Пароль"
            type="password"
            error={errors.password?.message}
            {...formRegister('password')}
          />
          {error && <p className="text-sm text-red-500">{error.message}</p>}
          <Button type="submit" loading={isPending} className="mt-2 w-full">
            Зарегистрироваться
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-500">
          Уже есть аккаунт?{' '}
          <Link to="/login" className="text-blue-600 hover:underline">
            Войти
          </Link>
        </p>
      </div>
    </div>
  )
}
