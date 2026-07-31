/**
 * A single labeled stat in a details grid (departure time, duration,
 * star rating, ...) — label above, value below. Distinct from InfoRow
 * (label-left/value-right, used for single-column lists) because a grid
 * of side-by-side label/value pairs reads poorly at narrow widths.
 */
export default function StatItem({ label, value }) {
  if (value == null || value === '') return null

  return (
    <div>
      <dt className="text-[11px] font-medium tracking-wide text-ink-muted uppercase">{label}</dt>
      <dd className="text-sm font-medium text-ink">{value}</dd>
    </div>
  )
}
