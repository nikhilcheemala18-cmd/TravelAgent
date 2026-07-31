/**
 * A single clickable trip suggestion on the welcome screen. Clicking
 * populates the chat input (via `onClick`) — it never sends on its own.
 */
export default function SuggestionChip({ children, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="border-border bg-card text-ink shadow-card hover:border-primary hover:bg-primary/5 hover:text-primary hover:shadow-card-hover rounded-full border px-4 py-2 text-sm transition hover:-translate-y-0.5"
    >
      {children}
    </button>
  )
}
