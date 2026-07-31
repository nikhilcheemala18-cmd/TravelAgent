import StatItem from '../common/StatItem'
import Badge from '../common/Badge'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatFieldLabel } from '../../utils/formatFieldLabel'
import { formatCabinClass, formatStops } from '../../utils/travelLabels'

// Fields given their own dedicated layout below. Anything else the
// backend adds to a flight option later still renders automatically via
// the generic loop — no card change needed, and nothing here assumes a
// specific provider's field set.
const FEATURED_FIELDS = new Set([
  'airline',
  'flight_number',
  'departure_time',
  'arrival_time',
  'price',
  'currency',
  'duration',
  'cabin_class',
  'stops',
])

// Cheapest/Fastest/Best Value map to green/amber/blue per the design spec.
const BADGE_TONE = { Cheapest: 'success', Fastest: 'warning', 'Best Value': 'primary' }

export default function FlightCard({ flight, badges = [] }) {
  if (!flight) return null

  const {
    airline,
    flight_number: flightNumber,
    departure_time: departureTime,
    arrival_time: arrivalTime,
    duration,
    price,
    currency,
    cabin_class: cabinClass,
    stops,
  } = flight

  const extraFields = Object.entries(flight).filter(
    ([key, value]) => !FEATURED_FIELDS.has(key) && value != null && value !== '',
  )

  return (
    <div className="group border-border bg-card shadow-card hover:shadow-card-hover rounded-xl border p-4 transition hover:-translate-y-0.5 sm:p-5">
      {badges.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          {badges.map((label) => (
            <Badge key={label} tone={BADGE_TONE[label] ?? 'neutral'}>
              {label}
            </Badge>
          ))}
        </div>
      )}

      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-ink font-semibold">{airline || 'Flight option'}</p>
          {flightNumber && <p className="text-ink-muted text-xs">Flight {flightNumber}</p>}
        </div>
        {price != null && (
          <p className="text-ink text-lg font-bold whitespace-nowrap">
            {formatCurrency(price, currency)}
          </p>
        )}
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-3">
        <StatItem label="Departs" value={departureTime} />
        <StatItem label="Arrives" value={arrivalTime} />
        <StatItem label="Duration" value={duration} />
        <StatItem label="Stops" value={stops != null ? formatStops(stops) : null} />
        <StatItem label="Cabin" value={cabinClass ? formatCabinClass(cabinClass) : null} />
        {extraFields.map(([key, value]) => (
          <StatItem key={key} label={formatFieldLabel(key)} value={String(value)} />
        ))}
      </dl>
    </div>
  )
}
