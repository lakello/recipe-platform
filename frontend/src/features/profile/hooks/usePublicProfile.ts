import { useQuery } from '@tanstack/react-query'
import { profileApi } from '../api/profileApi'

export function usePublicProfile(userId: string) {
  return useQuery({
    queryKey: ['publicUser', userId],
    queryFn: () => profileApi.getPublicUser(userId),
  })
}
