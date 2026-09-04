/**
 * The backend sends naive datetimes (UTC, but with no `Z`/offset suffix -
 * e.g. `"2026-09-04T22:34:57.869648"`). `new Date(...)` on a string like
 * that is parsed as *local* time, not UTC, silently shifting it by the
 * viewer's UTC offset. Force it back to UTC before doing any arithmetic
 * with it.
 */
export function parseUtcDate(isoString: string): Date {
  const hasTimezone = /Z$|[+-]\d{2}:?\d{2}$/.test(isoString)
  return new Date(hasTimezone ? isoString : `${isoString}Z`)
}

/** Remaining time until `expiredAtIso`, floored to whole minutes. */
export function formatExpiresIn(expiredAtIso: string): string {
  const minutes = Math.floor((parseUtcDate(expiredAtIso).getTime() - Date.now()) / 60_000)

  if (minutes <= 0) {
    return 'меньше минуты'
  }
  return `${minutes} мин.`
}
