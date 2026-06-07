import { useFollow } from '../hooks/useFollows'
import { Button } from '@/shared/ui/Button'

interface FollowButtonProps {
  userId: string
  isFollowing: boolean
}

export function FollowButton({ userId, isFollowing }: FollowButtonProps) {
  const { follow, unfollow } = useFollow(userId)
  const isPending = follow.isPending || unfollow.isPending

  if (isFollowing) {
    return (
      <Button
        variant="secondary"
        loading={isPending}
        onClick={() => unfollow.mutate()}
      >
        Отписаться
      </Button>
    )
  }

  return (
    <Button loading={isPending} onClick={() => follow.mutate()}>
      Подписаться
    </Button>
  )
}
