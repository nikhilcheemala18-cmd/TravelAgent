// Tone -> color mapping follows the spec exactly: Cheapest/Budget green,
// Fastest amber, Best Value/Mid-range blue, Premium purple. All colors
// come from the theme (src/styles/index.css) — never a raw hex here.
const TONE_CLASSES = {
  primary: 'border-primary/20 bg-primary/10 text-primary',
  success: 'border-success/20 bg-success/10 text-success',
  warning: 'border-warning/20 bg-warning/10 text-warning',
  premium: 'border-premium/20 bg-premium/10 text-premium',
  neutral: 'border-border bg-surface text-ink-muted',
}

/**
 * Small pill used for recommendation badges (Cheapest, Budget, ...) and
 * amenity chips alike — one component, different `tone`s, so badge and
 * chip styling never drifts apart or gets duplicated per card.
 */
export default function Badge({ children, tone = 'neutral' }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-medium whitespace-nowrap ${
        TONE_CLASSES[tone] ?? TONE_CLASSES.neutral
      }`}
    >
      {children}
    </span>
  )
}
