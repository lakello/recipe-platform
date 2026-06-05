import { useMutation, useQueryClient } from '@tanstack/react-query'
import { profileApi, type UpdateProfileData } from '../api/profileApi'
import { CURRENT_USER_KEY } from './useCurrentUser'

export function useUpdateProfile() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: UpdateProfileData) => profileApi.updateMe(data),
    onSuccess: (updated) => {
      queryClient.setQueryData(CURRENT_USER_KEY, updated)
    },
  })
}
