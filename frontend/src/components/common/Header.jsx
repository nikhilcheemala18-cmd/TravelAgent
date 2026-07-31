import { RotateCcw } from 'lucide-react'

export default function Header({ onNewTrip, hasConversation }) {
  return (
    <header className="border-border bg-card flex items-center justify-between border-b px-6 py-4 shadow-sm">
      <h1 className="text-ink text-xl font-bold tracking-tight">Flyo Travel Assistant</h1>
      {hasConversation && (
        <button
          type="button"
          onClick={onNewTrip}
          className="border-border text-ink-muted hover:bg-background hover:text-ink bg-card flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-medium transition"
        >
          <RotateCcw className="h-4 w-4" aria-hidden="true" />
          Start New Trip
        </button>
      )}
    </header>
  )
}
