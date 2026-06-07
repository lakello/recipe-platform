import { Link } from 'react-router-dom'

interface UserLinkProps {
  userId: string
  username: string
  avatarUrl: string | null
  size?: 'sm' | 'md'
}

export function UserLink({ userId, username, avatarUrl, size = 'sm' }: UserLinkProps) {
  const avatarClass = size === 'sm' ? 'w-7 h-7' : 'w-10 h-10'
  const textClass = size === 'sm' ? 'text-sm text-gray-500' : 'text-base text-gray-700 font-medium'
  const initialClass = size === 'sm' ? 'text-xs' : 'text-sm'

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
    </Link>
  )
}
