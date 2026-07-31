import { useEffect, useState } from 'react'

const DEFAULT_MESSAGES = [
  'Searching flights...',
  'Looking for hotels...',
  'Comparing options...',
  'Building your itinerary...',
]

/**
 * Cycles through `messages` on an interval while `active` is true, showing
 * exactly one at a time, resetting back to the first whenever a new
 * loading sequence starts. Purely a presentation timer — the backend
 * returns one response, not a stream of progress events; this just gives
 * the wait something reassuring to look at.
 */
export function useProgressiveLoadingMessage(active, messages = DEFAULT_MESSAGES, intervalMs = 1600) {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    if (!active) {
      setIndex(0)
      return undefined
    }

    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % messages.length)
    }, intervalMs)

    return () => clearInterval(timer)
  }, [active, messages, intervalMs])

  return messages[index]
}
