import { Navigate } from 'react-router-dom'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'

interface Props {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: Props) {
  const { data: user, isLoading } = useCurrentUser()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Загрузка...</p>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
