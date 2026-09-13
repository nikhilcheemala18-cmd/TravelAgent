import SuggestionChip from './SuggestionChip'

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
    <div className="animate-fade-in flex flex-1 flex-col items-center justify-center px-6 py-12 text-center">
      <h2 className="text-ink text-2xl font-bold">Hi! I&apos;m your AI Travel Assistant.</h2>
      <p className="text-ink-muted mt-3 max-w-sm text-sm leading-relaxed">
        Tell me where you&apos;d like to travel, and I&apos;ll help you plan your trip.
      </p>

      <div className="mt-6 flex max-w-xl flex-wrap justify-center gap-2">
        {SUGGESTIONS.map((suggestion) => (
          <SuggestionChip key={suggestion} onClick={() => onSuggestionClick(suggestion)}>
            {suggestion}
          </SuggestionChip>
        ))}
      </div>
    </div>
  )
}
