import SuggestionChip from './SuggestionChip'
import { Plane, MapPin, Compass, Hotel } from 'lucide-react'

const SUGGESTION_STYLES = [
  { label: 'Delhi to Paris for two', icon: Plane },
  { label: 'Explore Tokyo next Friday', icon: MapPin },
  { label: 'Change destination to Singapore', icon: Compass },
  { label: 'Mumbai to Goa with a 4-star stay', icon: Hotel },
]

const SUGGESTIONS = [
  'I want to travel from Delhi to Paris on 2026-11-20 for 2 passengers',
  'Travel to Tokyo next Friday',
  'Change destination to Singapore',
  'I want to travel from Mumbai to Goa on 2026-12-15 for 2 passengers with a 4-star hotel',
]

/**
 * Empty-state shown before the first message. `onSuggestionClick`
 * receives the suggestion text — the caller decides what to do with it
 * (populate the composer), this component owns no chat state itself.
 */
export default function WelcomeScreen({ onSuggestionClick }) {
  return (
    <div className="welcome-area animate-fade-in flex flex-1 flex-col items-center">
      <div className="welcome-intro">
        <h2 className="welcome-heading">Where to next?</h2>
        <p className="welcome-subheading">Tell me a destination, a date, or what you have in mind.</p>
      </div>

      <div className="suggestions-grid">
        {SUGGESTIONS.map((suggestion, index) => (
          <SuggestionChip key={suggestion} {...SUGGESTION_STYLES[index]} onClick={() => onSuggestionClick(suggestion)}>
            {suggestion}
          </SuggestionChip>
        ))}
      </div>
    </div>
  )
}
