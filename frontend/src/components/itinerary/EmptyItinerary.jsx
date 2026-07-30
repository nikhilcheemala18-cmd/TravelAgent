/**
 * Friendly placeholder shown before any itinerary exists, so the panel
 * never renders as dead empty space.
 */
export default function EmptyItinerary() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 py-16 text-center">
      <p className="text-sm font-medium text-gray-600">No trip planned yet</p>
      <p className="mt-1 max-w-xs text-sm text-gray-400">
        Tell the assistant where you&apos;d like to go, and your itinerary will show up here.
      </p>
    </div>
  )
}
