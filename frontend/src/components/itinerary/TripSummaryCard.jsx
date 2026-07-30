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
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm sm:p-5">
      <h3 className="mb-3 text-base font-semibold text-gray-900">Trip Summary</h3>
      <div className="flex flex-col gap-1.5">
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
          />
        )}
      </div>
    </div>
  )
}
