import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useSearchParams } from 'react-router-dom'
import { z } from 'zod'
import { useLogin } from '@/features/auth/hooks/useAuth'
import { Button } from '@/shared/ui/Button'
import { Input } from '@/shared/ui/Input'

const schema = z.object({
  email: z.string().email('Некорректный email'),
  password: z.string().min(1, 'Введите пароль'),
})

type FormData = z.infer<typeof schema>

const BACKEND_URL = import.meta.env.VITE_API_URL ?? ''

export function LoginPage() {
  const { mutate: login, isPending, error } = useLogin()
  const [searchParams] = useSearchParams()
  const oauthError = searchParams.get('error') === 'oauth_error'
    ? (searchParams.get('message') ?? 'Ошибка входа через OAuth')
    : null
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
          {oauthError && <p className="text-sm text-red-500">{oauthError}</p>}
          <Button type="submit" loading={isPending} className="mt-2 w-full">
            Войти
          </Button>
        </form>

        <div className="mt-4 flex flex-col gap-2">
          <div className="relative flex items-center">
            <div className="flex-grow border-t border-gray-200" />
            <span className="mx-3 flex-shrink text-xs text-gray-400">или</span>
            <div className="flex-grow border-t border-gray-200" />
          </div>
          <a
            href={`${BACKEND_URL}/api/auth/google/login`}
            className="flex w-full items-center justify-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          >
            <GoogleIcon />
            Войти через Google
          </a>
          <a
            href={`${BACKEND_URL}/api/auth/yandex/login`}
            className="flex w-full items-center justify-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          >
            <YandexIcon />
            Войти через Яндекс
          </a>
        </div>

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

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908C16.658 14.121 17.64 11.834 17.64 9.2z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
      <path d="M3.964 10.706A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.706V4.962H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.038l3.007-2.332z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.962L3.964 7.294C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
    </svg>
  )
}

function YandexIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="24" height="24" rx="4" fill="#FC3F1D"/>
      <path d="M13.694 20H11.4V8.24H10.28C8.246 8.24 7.18 9.248 7.18 10.808c0 1.764.798 2.59 2.38 3.654L10.9 15.5 7.026 20H4.6l4.2-5.516C6.58 13.19 5.5 11.9 5.5 10.022c0-2.548 1.764-4.222 4.766-4.222H13.7V20h-.006z" fill="white"/>
    </svg>
  )
}
