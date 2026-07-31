/**
 * A single label/value line used inside itinerary cards. Renders nothing
 * for a missing value so callers can list every possible field without
 * conditionally checking each one themselves. `valueClassName` lets a
 * caller emphasize a specific row (e.g. Estimated Total in the accent
 * color) without a one-off variant of this component.
 */
export default function InfoRow({ label, value, valueClassName }) {
  if (value == null || value === '') return null

  return (
    <div className="flex items-baseline justify-between gap-4 text-sm">
      <span className="text-ink-muted">{label}</span>
      <span className={valueClassName ?? 'text-ink text-right font-medium'}>{value}</span>
    </div>
  )
}
