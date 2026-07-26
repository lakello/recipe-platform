import axe from 'axe-core'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { LoginPage } from './login-page'
import { RegisterPage } from './register-page'

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useLogin: () => ({ mutate: vi.fn(), isPending: false, error: null }),
  useRegister: () => ({ mutate: vi.fn(), isPending: false, error: null }),
}))

describe.each([
  ['login', <LoginPage />],
  ['register', <RegisterPage />],
])('%s page accessibility', (_name, page) => {
  it('has no detectable axe violations', async () => {
    const { container } = render(<MemoryRouter>{page}</MemoryRouter>)
    const result = await axe.run(container, {
      rules: { 'color-contrast': { enabled: false } },
    })
    expect(result.violations).toEqual([])
  })
})
