import { afterEach, describe, expect, it, vi } from 'vitest'
import { apiFetch, apiJson } from './client'

function response(status: number, body: unknown = {}) {
  return new Response(status === 204 ? null : JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('api client', () => {
  it('shares one refresh between parallel 401 responses and retries each request once', async () => {
    let protectedCalls = 0
    let refreshCalls = 0
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: string | URL | Request) => {
        const url = String(input)
        if (url.endsWith('/api/auth/refresh')) {
          refreshCalls += 1
          return response(204)
        }
        protectedCalls += 1
        return protectedCalls <= 2 ? response(401) : response(200)
      }),
    )

    const results = await Promise.all([apiFetch('/one'), apiFetch('/two')])

    expect(results.map((result) => result.status)).toEqual([200, 200])
    expect(refreshCalls).toBe(1)
    expect(protectedCalls).toBe(4)
  })

  it('does not enter a second refresh loop', async () => {
    let refreshCalls = 0
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: string | URL | Request) => {
        if (String(input).endsWith('/api/auth/refresh')) {
          refreshCalls += 1
          return response(204)
        }
        return response(401)
      }),
    )

    expect((await apiFetch('/protected')).status).toBe(401)
    expect(refreshCalls).toBe(1)
  })

  it('normalizes validation errors', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => response(422, { detail: [{ msg: 'required' }] })),
    )

    await expect(apiJson('/form')).rejects.toMatchObject({
      kind: 'validation',
      status: 422,
      details: [{ msg: 'required' }],
    })
  })
})
