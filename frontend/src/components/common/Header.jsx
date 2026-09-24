import { RotateCcw } from 'lucide-react'
import TravelMark from './TravelMark'

export default function Header({ onNewTrip, hasConversation }) {
  return (
    <header className="app-header">
      <div className="brand-lockup">
        <TravelMark />
        <h1>
          <span className="brand-name">flyo</span>
          <span className="brand-description">Travel Assistant</span>
        </h1>
      </div>
      {hasConversation && (
        <button
          type="button"
          onClick={onNewTrip}
          className="new-trip-button"
        >
          <RotateCcw className="h-4 w-4" aria-hidden="true" />
          Start New Trip
        </button>
      )}
    </header>
  )
}
