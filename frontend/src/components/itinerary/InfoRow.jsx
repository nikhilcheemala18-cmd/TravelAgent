/**
 * A single label/value line used inside itinerary cards. Renders nothing
 * for a missing value so callers can list every possible field without
 * conditionally checking each one themselves.
 */
export default function InfoRow({ label, value }) {
  if (value == null || value === '') return null

  return (
    <div className="flex items-baseline justify-between gap-4 text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="text-right font-medium text-gray-900">{value}</span>
    </div>
  )
}
