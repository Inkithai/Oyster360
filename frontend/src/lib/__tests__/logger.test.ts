import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  configureLogger,
  getLoggerConfig,
  logger,
  parseDsn,
  reportError,
} from '../logger'

describe('logger', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
    vi.spyOn(console, 'log').mockImplementation(() => {})
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    vi.spyOn(console, 'error').mockImplementation(() => {})
    configureLogger({ level: 'debug', dsn: null, release: null, environment: 'test' })
  })

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
  })

  it('emits structured JSON entries for enabled levels', () => {
    logger.info('page_viewed', { page: '/dashboard' })

    const raw = (console.log as ReturnType<typeof vi.fn>).mock.calls.at(-1)?.[1] as string
    const entry = JSON.parse(raw)
    expect(entry.level).toBe('info')
    expect(entry.event).toBe('page_viewed')
    expect(entry.page).toBe('/dashboard')
    expect(entry.timestamp).toBeTruthy()
  })

  it('suppresses entries below the configured level', () => {
    configureLogger({ level: 'warn' })
    logger.debug('noisy_event')
    logger.info('also_hidden')

    expect(console.log).not.toHaveBeenCalled()
  })

  it('routes warnings and errors to the matching console sink', () => {
    logger.warn('slow_query', { ms: 900 })
    logger.error('boom')

    expect(console.warn).toHaveBeenCalledOnce()
    expect(console.error).toHaveBeenCalledOnce()
  })

  it('configureLogger persists and returns the active config', () => {
    configureLogger({ dsn: 'https://key@sentry.example.com/42' })
    expect(getLoggerConfig().dsn).toBe('https://key@sentry.example.com/42')
  })
})

describe('parseDsn', () => {
  it('parses a Sentry DSN into an envelope endpoint', () => {
    const parsed = parseDsn('https://abc123@o1.ingest.sentry.io/456')
    expect(parsed).toEqual({
      url: 'https://o1.ingest.sentry.io/api/456/envelope/',
      publicKey: 'abc123',
    })
  })

  it('rejects malformed DSNs', () => {
    expect(parseDsn('not-a-dsn')).toBeNull()
    expect(parseDsn('')).toBeNull()
  })
})

describe('reportError', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    configureLogger({ dsn: null, level: 'debug' })
  })

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
    configureLogger({ dsn: null })
  })

  it('logs the error locally even without a DSN', async () => {
    const result = reportError(new Error('offline failure'))

    expect(result).toBeNull()
    expect(console.error).toHaveBeenCalled()
  })

  it('posts a Sentry envelope when a DSN is configured', async () => {
    const fetchMock = vi.fn(async () => ({ ok: true }) as unknown as Response)
    global.fetch = fetchMock as unknown as typeof fetch
    configureLogger({ dsn: 'https://abc123@o1.ingest.sentry.io/456' })

    await reportError(new Error('payment_failed'), { checkout_id: 'cs_1' })

    expect(fetchMock).toHaveBeenCalledOnce()
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit]
    expect(url).toBe('https://o1.ingest.sentry.io/api/456/envelope/')
    expect((init.headers as Record<string, string>)['X-Sentry-Auth']).toContain('abc123')
    expect(String(init.body)).toContain('payment_failed')
    expect(String(init.body)).toContain('cs_1')
  })

  it('degrades gracefully when the transport fails', async () => {
    global.fetch = vi.fn(async () => {
      throw new TypeError('network down')
    }) as unknown as typeof fetch
    configureLogger({ dsn: 'https://abc123@o1.ingest.sentry.io/456' })

    const result = await reportError(new Error('still reported locally'))

    expect(result).toBeNull()
    expect(console.warn).toHaveBeenCalled()
  })
})
