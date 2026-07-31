import { parseDurationToMinutes } from './parseDuration'

/**
 * Compute presentation-only "Cheapest" / "Fastest" / "Best Value" badges
 * for a list of flight options. This is purely a frontend display
 * heuristic — the backend doesn't tag individual options, so these badges
 * only ever mean "best among what's currently shown."
 *
 * "Best Value" favors the fewest stops (tie-broken by price), since the
 * cheapest option isn't necessarily the one worth recommending if it has
 * two layovers.
 *
 * Returns an array parallel to `flights`; each entry is the list of badge
 * labels for that flight (often empty, sometimes more than one).
 */
export function getFlightBadges(flights) {
  const badges = flights.map(() => [])
  if (!flights.length) return badges

  let cheapestIndex = 0
  let fastestIndex = 0
  let bestValueIndex = 0
  let cheapestPrice = Infinity
  let fastestMinutes = Infinity
  let bestValueScore = Infinity

  flights.forEach((flight, index) => {
    const price = flight.price ?? Infinity
    const minutes = parseDurationToMinutes(flight.duration)
    const stops = flight.stops ?? 0
    const valueScore = stops * 100000 + price

    if (price < cheapestPrice) {
      cheapestPrice = price
      cheapestIndex = index
    }
    if (minutes < fastestMinutes) {
      fastestMinutes = minutes
      fastestIndex = index
    }
    if (valueScore < bestValueScore) {
      bestValueScore = valueScore
      bestValueIndex = index
    }
  })

  badges[cheapestIndex].push('Cheapest')
  badges[fastestIndex].push('Fastest')
  if (bestValueIndex !== cheapestIndex) {
    badges[bestValueIndex].push('Best Value')
  }

  return badges
}
