import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { CURRENT_USER_KEY } from '@/features/profile/hooks/useCurrentUser'
import { authApi, type LoginData, type RegisterData } from '../api/authApi'

export function useRegister() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return useMutation({
    mutationFn: (data: RegisterData) => authApi.register(data),
    onSuccess: async () => {
      await queryClient.refetchQueries({ queryKey: CURRENT_USER_KEY })
      navigate('/')
    },
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return useMutation({
    mutationFn: (data: LoginData) => authApi.login(data),
    onSuccess: async () => {
      await queryClient.refetchQueries({ queryKey: CURRENT_USER_KEY })
      void queryClient.invalidateQueries({ queryKey: ['notifications'] })
      navigate('/')
    },
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  return useMutation({
    mutationFn: authApi.logout,
    onSettled: () => {
      queryClient.setQueryData(CURRENT_USER_KEY, null)
      queryClient.removeQueries({ queryKey: ['notifications'] })
      navigate('/login')
    },
  })
}
