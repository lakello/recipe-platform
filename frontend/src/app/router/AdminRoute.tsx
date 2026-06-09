import { Navigate } from 'react-router-dom'
import { useCurrentUser } from '@/features/profile/hooks/useCurrentUser'

interface Props {
  children: React.ReactNode
  minRole?: 'moderator' | 'admin' | 'superadmin'
}

export function AdminRoute({ children, minRole = 'moderator' }: Props) {
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

  const roleOrder = ['user', 'moderator', 'admin', 'superadmin']
  const userLevel = roleOrder.indexOf(user.role)
  const requiredLevel = roleOrder.indexOf(minRole)

  if (userLevel < requiredLevel) {
    return <Navigate to="/recipes" replace />
  }

  return <>{children}</>
}
