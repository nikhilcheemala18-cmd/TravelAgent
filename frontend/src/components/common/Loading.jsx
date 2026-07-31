/**
 * Animated three-dot loading indicator with a label. Used two ways: as
 * the chat's typing indicator (label kept for screen readers only, dots
 * are the visible cue) and as the itinerary panel's progressive-message
 * loading state (label visible, cycling text). One component so the
 * visual treatment can't drift between the two uses.
 */
export default function Loading({ label = 'Loading...', visibleLabel = true }) {
  return (
    <div className="flex items-center gap-2 text-sm text-ink-muted" role="status" aria-live="polite">
      <span className="flex items-center gap-1">
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-muted [animation-delay:-0.3s]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-muted [animation-delay:-0.15s]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-muted" />
      </span>
      <span className={visibleLabel ? 'transition-opacity duration-200' : 'sr-only'}>{label}</span>
    </div>
  )
}
