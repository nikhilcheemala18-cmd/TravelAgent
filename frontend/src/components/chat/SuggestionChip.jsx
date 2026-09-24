/**
 * A single clickable trip suggestion on the welcome screen. Clicking
 * populates the chat input (via `onClick`) — it never sends on its own.
 */
export default function SuggestionChip({ children, onClick, icon: Icon, label }) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={children}
      className="suggestion-card text-ink hover:border-primary hover:shadow-card-hover transition hover:-translate-y-0.5"
    >
      {Icon && <Icon className="suggestion-icon" aria-hidden="true" />}
      <span className="suggestion-label">{label}</span>
    </button>
  )
}
