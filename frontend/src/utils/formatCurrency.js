/**
 * Format a numeric amount + ISO currency code as a localized currency
 * string. Falls back to a plain "<amount> <currency>" string if the
 * currency code isn't one Intl recognizes, rather than throwing.
 */
export function formatCurrency(amount, currency = 'USD') {
  if (amount == null) return null

  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency,
      maximumFractionDigits: 2,
    }).format(amount)
  } catch {
    return `${amount} ${currency}`
  }
}
