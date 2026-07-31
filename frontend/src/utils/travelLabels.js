import { formatFieldLabel } from './formatFieldLabel'

// Explicit lookup because these enum values aren't snake_case-splittable
// into their natural display form (e.g. "guesthouse" has no underscore
// to split on but should read "Guest House"). Falls back to the generic
// formatter for anything not listed, so a future backend enum value still
// renders as *something* readable rather than being dropped.
const HOTEL_TYPE_LABELS = {
  hotel: 'Hotel',
  resort: 'Resort',
  boutique: 'Boutique',
  hostel: 'Hostel',
  apartment: 'Apartment',
  guesthouse: 'Guest House',
}

const CABIN_CLASS_LABELS = {
  economy: 'Economy',
  premium_economy: 'Premium Economy',
  business: 'Business',
  first: 'First Class',
}

export function formatHotelType(value) {
  if (!value) return ''
  return HOTEL_TYPE_LABELS[value] ?? formatFieldLabel(value)
}

export function formatCabinClass(value) {
  if (!value) return ''
  return CABIN_CLASS_LABELS[value] ?? formatFieldLabel(value)
}

export function formatStops(stops) {
  if (stops === 0) return 'Nonstop'
  if (stops === 1) return '1 stop'
  return `${stops} stops`
}
