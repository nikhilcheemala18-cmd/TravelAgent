/**
 * Classify a hotel into a Budget / Mid-range / Premium presentation badge
 * based on nightly price. HotelOption has no explicit tier field from the
 * backend, so this is a frontend-only display heuristic (loosely mirroring
 * the mock provider's own price bands) — not a backend contract.
 */
const BUDGET_MAX = 90
const MID_RANGE_MAX = 200

export function getHotelTierBadge(hotel) {
  if (hotel?.price_per_night == null) return null
  if (hotel.price_per_night < BUDGET_MAX) return 'Budget'
  if (hotel.price_per_night < MID_RANGE_MAX) return 'Mid-range'
  return 'Premium'
}
