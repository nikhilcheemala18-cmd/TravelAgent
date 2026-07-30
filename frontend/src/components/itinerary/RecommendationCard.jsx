/**
 * A single recommendation string from the backend, rendered as its own
 * card — kept out of the chat transcript so recommendations read as
 * itinerary content, not conversation.
 */
export default function RecommendationCard({ text }) {
  if (!text) return null

  return (
    <div className="rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-900">
      {text}
    </div>
  )
}
