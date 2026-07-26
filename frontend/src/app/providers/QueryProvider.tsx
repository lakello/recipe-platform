import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { type ReactNode } from 'react'
import { ApiError } from '@/shared/api/client'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) =>
        failureCount < 1 &&
        error instanceof ApiError &&
        ['offline', 'rate_limit', 'unavailable'].includes(error.kind),
      staleTime: 30_000,
      gcTime: 5 * 60_000,
    },
  },
})

interface Props {
  children: ReactNode
}

export function QueryProvider({ children }: Props) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}
