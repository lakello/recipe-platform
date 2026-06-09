import { Link } from 'react-router-dom'
import type { UserRole } from '@/features/profile/api/profileApi'

const ROLE_BADGE: Record<string, string> = {
  moderator: 'bg-yellow-100 text-yellow-800',
  admin: 'bg-red-100 text-red-700',
  superadmin: 'bg-purple-100 text-purple-700',
}

interface UserLinkProps {
  userId: string
  username: string
  avatarUrl: string | null
  role?: UserRole | string
  size?: 'sm' | 'md'
}

export function UserLink({ userId, username, avatarUrl, role, size = 'sm' }: UserLinkProps) {
  const avatarClass = size === 'sm' ? 'w-7 h-7' : 'w-10 h-10'
  const textClass = size === 'sm' ? 'text-sm text-gray-500' : 'text-base text-gray-700 font-medium'
  const initialClass = size === 'sm' ? 'text-xs' : 'text-sm'
  const badgeStyle = role && ROLE_BADGE[role] ? ROLE_BADGE[role] : null

  return (
    <Link
      to={`/users/${userId}`}
      onClick={(e) => e.stopPropagation()}
      className="flex items-center gap-2 hover:opacity-75 transition-opacity"
    >
      {avatarUrl ? (
        <img
          src={avatarUrl}
          alt={username}
          className={`${avatarClass} rounded-full object-cover shrink-0`}
        />
      ) : (
        <div className={`${avatarClass} rounded-full bg-blue-100 flex items-center justify-center shrink-0`}>
          <span className={`${initialClass} font-semibold text-blue-600 uppercase`}>
            {username.charAt(0)}
          </span>
        </div>
      )}
      <span className={textClass}>{username}</span>
      {badgeStyle && (
        <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${badgeStyle}`}>
          {role}
        </span>
      )}
    </Link>
  )
}
