import { MapPinned } from 'lucide-react'
import InfoRow from './InfoRow'
import { formatCurrency } from '../../utils/formatCurrency'

const TRAVELER_FIELDS = [
  ['origin', 'Origin'],
  ['destination', 'Destination'],
  ['departure_date', 'Departure Date'],
  ['return_date', 'Return Date'],
  ['passengers', 'Passengers'],
]

/**
 * Summarizes the confirmed trip parameters (backend `traveler_information`)
 * plus the computed `trip_summary.total_estimated_cost`, when available.
 */
export default function TripSummaryCard({ travelerInfo, tripSummary }) {
  if (!travelerInfo) return null

  const currency = tripSummary?.currency

  return (
    <div className="trip-summary-card animate-fade-in border-border bg-card shadow-card rounded-xl border p-4 sm:p-5">
      <h3 className="text-ink mb-4 flex items-center gap-2 text-base font-semibold">
        <MapPinned className="text-primary h-5 w-5" aria-hidden="true" />
        Trip Summary
      </h3>
      <div className="trip-summary-fields flex flex-col">
        {TRAVELER_FIELDS.map(([key, label]) => (
          <InfoRow key={key} label={label} value={travelerInfo[key]} />
        ))}
        <InfoRow
          label="Budget"
          value={travelerInfo.budget != null ? formatCurrency(travelerInfo.budget, currency) : null}
        />
        <InfoRow
          label="Hotel Rating"
          value={travelerInfo.hotel_rating != null ? `${travelerInfo.hotel_rating}-star` : null}
        />
        {tripSummary?.total_estimated_cost != null && (
          <InfoRow
            label="Estimated Total"
            value={formatCurrency(tripSummary.total_estimated_cost, currency)}
            rowClassName="trip-summary-total"
            valueClassName="text-accent text-right text-lg font-semibold"
          />
        )}
      </div>
    </div>
  )
}
