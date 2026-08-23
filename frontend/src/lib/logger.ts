/**
 * Structured frontend logging and error reporting.
 *
 * Mirrors the backend's JSON log lines: every entry carries a level, an
 * event name, and a context object, and error reports are forwarded to a
 * Sentry-compatible envelope endpoint when NEXT_PUBLIC_SENTRY_DSN is set.
 * With no DSN configured the logger degrades to console output only, so
 * local development and tests never touch the network.
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error'

export interface LogContext {
  [key: string]: unknown
}

export interface LoggerConfig {
  level: LogLevel
  dsn: string | null
  release: string | null
  environment: string
}

const LEVEL_WEIGHT: Record<LogLevel, number> = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
}

let config: LoggerConfig = {
  level: 'info',
  dsn: null,
  release: null,
  environment: process.env.NODE_ENV ?? 'development',
}

/** Overwrite defaults (used by tests and app bootstrap). */
export function configureLogger(overrides: Partial<LoggerConfig> = {}): LoggerConfig {
  config = { ...config, ...overrides }
  return config
}

export function getLoggerConfig(): LoggerConfig {
  return config
}

function write(level: LogLevel, event: string, context: LogContext = {}): void {
  if (LEVEL_WEIGHT[level] < LEVEL_WEIGHT[config.level]) {
    return
  }

  const entry = {
    timestamp: new Date().toISOString(),
    level,
    event,
    environment: config.environment,
    release: config.release,
    ...context,
  }

  const sink = level === 'error' ? console.error : level === 'warn' ? console.warn : console.log
  sink(`[oyster360] ${event}`, JSON.stringify(entry))
}

export const logger = {
  debug: (event: string, context?: LogContext) => write('debug', event, context),
  info: (event: string, context?: LogContext) => write('info', event, context),
  warn: (event: string, context?: LogContext) => write('warn', event, context),
  error: (event: string, context?: LogContext) => write('error', event, context),
}

export interface ParsedDsn {
  url: string
  publicKey: string
}

/** Parse `https://key@host/project` into a Sentry envelope endpoint. */
export function parseDsn(dsn: string): ParsedDsn | null {
  const match = /^https:\/\/([^@]+)@([^/]+)\/(\d+)$/.exec(dsn)
  if (!match) {
    return null
  }
  const [, publicKey, host, projectId] = match
  return { url: `https://${host}/api/${projectId}/envelope/`, publicKey }
}

interface ReportedError {
  message: string
  stack?: string
}

/**
 * Forward an error to the configured Sentry-compatible endpoint.
 * Returns the fetch promise when reporting, or null when disabled so
 * callers can await safely without branching.
 */
export function reportError(error: ReportedError, context: LogContext = {}): Promise<unknown> | null {
  logger.error('client_error', { message: error.message, ...context })

  if (!config.dsn || typeof window === 'undefined') {
    return null
  }
  const parsed = parseDsn(config.dsn)
  if (!parsed) {
    logger.warn('sentry_dsn_invalid', { dsn: config.dsn })
    return null
  }

  const envelope = [
    JSON.stringify({ event_id: crypto.randomUUID(), sent_at: new Date().toISOString() }),
    JSON.stringify({ type: 'error' }),
    JSON.stringify({
      level: 'error',
      environment: config.environment,
      release: config.release,
      message: { formatted: error.message },
      stacktrace: error.stack ? { frames: [] } : undefined,
      extra: context,
    }),
  ].join('\n')

  return fetch(parsed.url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-sentry-envelope',
      'X-Sentry-Auth': `Sentry sentry_version=7, sentry_key=${parsed.publicKey}`,
    },
    body: envelope,
    keepalive: true,
  }).catch((transportError: unknown) => {
    write('warn', 'sentry_report_failed', {
      reason: transportError instanceof Error ? transportError.message : String(transportError),
    })
    return null
  })
}
