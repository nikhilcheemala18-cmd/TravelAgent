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
      className="animate-fade-in border-warning/30 bg-warning/10 text-ink rounded-lg border px-4 py-3 text-sm"
    >
      {text}
    </div>
  )
}
