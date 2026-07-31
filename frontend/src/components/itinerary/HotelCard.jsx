import { Star } from 'lucide-react'
import StatItem from '../common/StatItem'
import Badge from '../common/Badge'
import { formatCurrency } from '../../utils/formatCurrency'
import { formatFieldLabel } from '../../utils/formatFieldLabel'
import { formatHotelType } from '../../utils/travelLabels'
import { getHotelTierBadge } from '../../utils/hotelTier'

// See FlightCard for why unlisted fields still render automatically.
const FEATURED_FIELDS = new Set([
  'name',
  'star_rating',
  'price_per_night',
  'currency',
  'amenities',
  'location',
  'review_score',
  'hotel_type',
])

// Budget/Mid-range/Premium map to green/blue/purple per the design spec.
const TIER_TONE = { Budget: 'success', 'Mid-range': 'primary', Premium: 'premium' }

export default function HotelCard({ hotel }) {
  if (!hotel) return null

  const {
    name,
    star_rating: starRating,
    price_per_night: pricePerNight,
    currency,
    amenities,
    location,
    review_score: reviewScore,
    hotel_type: hotelType,
  } = hotel

  const tier = getHotelTierBadge(hotel)
  const extraFields = Object.entries(hotel).filter(
    ([key, value]) => !FEATURED_FIELDS.has(key) && value != null && value !== '',
  )

  return (
    <div className="group border-border bg-card shadow-card hover:shadow-card-hover rounded-xl border p-4 transition hover:-translate-y-0.5 sm:p-5">
      {(tier || hotelType) && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          {tier && <Badge tone={TIER_TONE[tier]}>{tier}</Badge>}
          {hotelType && <Badge tone="neutral">{formatHotelType(hotelType)}</Badge>}
        </div>
      )}

      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-ink font-semibold">{name || 'Hotel option'}</p>
          <div className="text-ink-muted mt-1 flex flex-wrap items-center gap-x-2 text-xs">
            {starRating != null && (
              <span className="text-gold inline-flex items-center gap-0.5 font-medium">
                <Star className="h-3.5 w-3.5 fill-current" aria-hidden="true" />
                {starRating}
              </span>
            )}
            {reviewScore != null && <span>&middot; {reviewScore}/10 reviews</span>}
            {location && <span>&middot; {location}</span>}
          </div>
        </div>
        {pricePerNight != null && (
          <p className="text-ink text-lg font-bold whitespace-nowrap">
            {formatCurrency(pricePerNight, currency)}
            <span className="text-ink-muted ml-1 text-xs font-normal">/night</span>
          </p>
        )}
      </div>

      {amenities?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {amenities.map((amenity) => (
            <Badge key={amenity} tone="neutral">
              {amenity}
            </Badge>
          ))}
        </div>
      )}

      {extraFields.length > 0 && (
        <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-3">
          {extraFields.map(([key, value]) => (
            <StatItem key={key} label={formatFieldLabel(key)} value={String(value)} />
          ))}
        </dl>
      )}
    </div>
  )
}
