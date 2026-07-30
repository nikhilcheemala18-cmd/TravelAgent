/**
 * A single warning/unavailable-service message, visually distinct from
 * both chat messages and recommendations (amber, alert role) so problems
 * stand out from normal itinerary content.
 */
export default function WarningCard({ text }) {
  if (!text) return null

  return (
    <div
      role="alert"
      className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {text}
    </div>
  )
}
