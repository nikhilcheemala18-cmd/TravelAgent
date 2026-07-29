/**
 * Static (non-animated) loading indicator — see Phase F1 scope notes on
 * not introducing animation yet.
 */
export default function Loading({ label = 'Assistant is typing...' }) {
  return (
    <div className="flex items-center gap-2 text-sm text-gray-500" role="status" aria-live="polite">
      <span className="inline-block h-2 w-2 rounded-full bg-gray-400" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}
