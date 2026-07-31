/**
 * Parse a backend duration string like "3h 41m" or "5h" into total minutes.
 * Returns Infinity for anything unparseable so it naturally sorts last
 * rather than winning a "fastest" comparison by accident.
 */
export function parseDurationToMinutes(duration) {
  if (!duration) return Infinity

  const hoursMatch = duration.match(/(\d+)\s*h/)
  const minutesMatch = duration.match(/(\d+)\s*m/)
  if (!hoursMatch && !minutesMatch) return Infinity

  const hours = hoursMatch ? Number(hoursMatch[1]) : 0
  const minutes = minutesMatch ? Number(minutesMatch[1]) : 0
  return hours * 60 + minutes
}
