import InfoRow from './InfoRow'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatFieldLabel } from '../../utils/formatFieldLabel'

// Fields given their own dedicated layout below. Anything else the
// backend adds to a flight option later (layovers, cabin class, ...)
// still renders automatically via the generic loop — no card change
// needed, and nothing here assumes a specific provider's field set.
const FEATURED_FIELDS = new Set([
  'airline',
  'flight_number',
  'departure_time',
  'arrival_time',
  'price',
  'currency',
])

export default function FlightCard({ flight }) {
  if (!flight) return null

  const { airline, flight_number: flightNumber, departure_time: departureTime, arrival_time: arrivalTime, price, currency } = flight

  const extraFields = Object.entries(flight).filter(
    ([key, value]) => !FEATURED_FIELDS.has(key) && value != null && value !== '',
  )

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-medium text-gray-900">{airline || 'Flight option'}</p>
          {flightNumber && <p className="text-xs text-gray-500">Flight {flightNumber}</p>}
        </div>
        {price != null && (
          <p className="whitespace-nowrap text-base font-semibold text-gray-900">
            {formatCurrency(price, currency)}
          </p>
        )}
      </div>

      <div className="mt-3 flex flex-col gap-1.5">
        <InfoRow label="Departs" value={departureTime} />
        <InfoRow label="Arrives" value={arrivalTime} />
        {extraFields.map(([key, value]) => (
          <InfoRow key={key} label={formatFieldLabel(key)} value={String(value)} />
        ))}
      </div>
    </div>
  )
}
