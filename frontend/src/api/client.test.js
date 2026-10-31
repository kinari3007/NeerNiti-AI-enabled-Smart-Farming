import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { http, ApiError } from './client'

function mockFetch(impl) {
  globalThis.fetch = vi.fn(impl)
}

function jsonResponse(body, { ok = true, status = 200 } = {}) {
  return {
    ok,
    status,
    text: async () => (body == null ? '' : JSON.stringify(body)),
  }
}

describe('http client', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('prefixes GET requests with /api/v1', async () => {
    mockFetch(async () => jsonResponse({ items: [] }))
    await http.get('/farms')
    expect(globalThis.fetch).toHaveBeenCalledWith('/api/v1/farms', expect.objectContaining({ method: 'GET' }))
  })

  it('serialises JSON bodies and sets content-type on POST', async () => {
    mockFetch(async () => jsonResponse({ id: 'f1' }, { status: 201 }))
    await http.post('/farms', { name: 'Test' })
    const [, opts] = globalThis.fetch.mock.calls[0]
    expect(opts.method).toBe('POST')
    expect(opts.headers['Content-Type']).toBe('application/json')
    expect(opts.body).toBe(JSON.stringify({ name: 'Test' }))
  })

  it('parses a JSON success body', async () => {
    mockFetch(async () => jsonResponse({ id: 'rec1', optimization_status: 'feasible' }))
    const data = await http.get('/recommendations/rec1')
    expect(data).toEqual({ id: 'rec1', optimization_status: 'feasible' })
  })

  it('throws ApiError with the backend message on error responses', async () => {
    mockFetch(async () =>
      jsonResponse({ error: 'NOT_FOUND', message: "Farm 'x' not found" }, { ok: false, status: 404 }),
    )
    await expect(http.get('/farms/x')).rejects.toMatchObject({
      name: 'ApiError',
      status: 404,
      code: 'NOT_FOUND',
      message: "Farm 'x' not found",
    })
  })

  it('classifies error types via ApiError getters', () => {
    expect(new ApiError('x', { status: 401 }).isAuthError).toBe(true)
    expect(new ApiError('x', { status: 403 }).isAuthError).toBe(true)
    expect(new ApiError('x', { status: 404 }).isNotFound).toBe(true)
    expect(new ApiError('x', { status: 0 }).isNetworkError).toBe(true)
    expect(new ApiError('x', { status: 500 }).isAuthError).toBe(false)
  })

  it('wraps fetch/network failures in a NETWORK_ERROR ApiError', async () => {
    mockFetch(async () => {
      throw new TypeError('Failed to fetch')
    })
    await expect(http.get('/farms')).rejects.toMatchObject({
      status: 0,
      code: 'NETWORK_ERROR',
    })
  })

  it('requests /health without the /api/v1 prefix', async () => {
    mockFetch(async () => jsonResponse({ status: 'ok' }))
    await http.health()
    expect(globalThis.fetch).toHaveBeenCalledWith('/health', expect.objectContaining({ method: 'GET' }))
  })
})
