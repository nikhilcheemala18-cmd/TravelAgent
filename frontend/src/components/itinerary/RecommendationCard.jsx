/**
 * A single recommendation string from the backend, rendered as its own
 * card — kept out of the chat transcript so recommendations read as
 * itinerary content, not conversation.
 */
export default function RecommendationCard({ text }) {
  if (!text) return null

  return (
    <div className="animate-fade-in border-primary/20 bg-primary/5 text-ink rounded-lg border px-4 py-3 text-sm">
      {text}
    </div>
  )
}
