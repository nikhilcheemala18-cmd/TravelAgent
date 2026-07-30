import InfoRow from './InfoRow'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatFieldLabel } from '../../utils/formatFieldLabel'

// See FlightCard for why unlisted fields still render automatically.
const FEATURED_FIELDS = new Set(['name', 'star_rating', 'price_per_night', 'currency'])

export default function HotelCard({ hotel }) {
  if (!hotel) return null

  const { name, star_rating: starRating, price_per_night: pricePerNight, currency } = hotel

  const extraFields = Object.entries(hotel).filter(
    ([key, value]) => !FEATURED_FIELDS.has(key) && value != null && value !== '',
  )

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-medium text-gray-900">{name || 'Hotel option'}</p>
          {starRating != null && <p className="text-xs text-gray-500">{starRating}-star</p>}
        </div>
        {pricePerNight != null && (
          <p className="whitespace-nowrap text-base font-semibold text-gray-900">
            {formatCurrency(pricePerNight, currency)}
            <span className="ml-1 text-xs font-normal text-gray-500">/night</span>
          </p>
        )}
      </div>

      {extraFields.length > 0 && (
        <div className="mt-3 flex flex-col gap-1.5">
          {extraFields.map(([key, value]) => (
            <InfoRow key={key} label={formatFieldLabel(key)} value={String(value)} />
          ))}
        </div>
      )}
    </div>
  )
}
