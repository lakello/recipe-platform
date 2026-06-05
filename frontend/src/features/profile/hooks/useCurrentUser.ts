import { useQuery } from '@tanstack/react-query'
import { profileApi } from '../api/profileApi'

export const CURRENT_USER_KEY = ['currentUser'] as const

export function useCurrentUser() {
  return useQuery({
    queryKey: CURRENT_USER_KEY,
    queryFn: profileApi.getMe,
    retry: false,
  })
}
