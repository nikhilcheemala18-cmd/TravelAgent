/**
 * Format an ISO timestamp as a short local time string for message bubbles.
 * Returns an empty string for anything that isn't a valid date, rather
 * than throwing.
 */
export function formatTimestamp(isoString) {
  if (!isoString) return ''
  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
