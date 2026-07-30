/**
 * Turn a snake_case API field name into a human-readable label, e.g.
 * "layover_count" -> "Layover Count". Used so cards can render fields the
 * backend adds later without any per-field code change.
 */
export function formatFieldLabel(key) {
  return key
    .split('_')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
