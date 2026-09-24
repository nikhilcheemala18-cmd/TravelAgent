import { MapPinned } from 'lucide-react'

/**
 * Friendly placeholder shown before any itinerary exists, so the panel
 * never renders as dead empty space.
 */
export default function EmptyItinerary() {
  return (
    <div className="animate-fade-in flex flex-1 flex-col items-center justify-center px-6 py-16 text-center">
      <div className="empty-trip-icon"><MapPinned aria-hidden="true" /></div>
      <p className="text-ink text-lg font-medium">Your trip starts here</p>
      <p className="text-ink-muted mt-1 max-w-xs text-sm">
        Your flight and hotel options will appear here.
      </p>
    </div>
  )
}
