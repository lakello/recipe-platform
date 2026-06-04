import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'
import { useLogin } from '@/features/auth/hooks/useAuth'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

const schema = z.object({
  email: z.string().email('Некорректный email'),
  password: z.string().min(1, 'Введите пароль'),
})

type FormData = z.infer<typeof schema>

export function LoginPage() {
  const { mutate: login, isPending, error } = useLogin()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-sm rounded-xl bg-white p-8 shadow-sm">
        <h1 className="mb-6 text-2xl font-bold text-gray-900">Вход</h1>
        <form onSubmit={handleSubmit((data) => login(data))} className="flex flex-col gap-4">
          <Input
            label="Email"
            type="email"
            error={errors.email?.message}
            {...register('email')}
          />
          <Input
            label="Пароль"
            type="password"
            error={errors.password?.message}
            {...register('password')}
          />
          {error && <p className="text-sm text-red-500">{error.message}</p>}
          <Button type="submit" loading={isPending} className="mt-2 w-full">
            Войти
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-500">
          Нет аккаунта?{' '}
          <Link to="/register" className="text-blue-600 hover:underline">
            Зарегистрироваться
          </Link>
        </p>
      </div>
    </div>
  )
}
