import { useState } from 'react'
import Header from '../components/common/Header'
import ErrorMessage from '../components/common/ErrorMessage'
import ChatWindow from '../components/chat/ChatWindow'
import ChatInput from '../components/chat/ChatInput'
import ItineraryPanel from '../components/itinerary/ItineraryPanel'
import { useChat } from '../hooks/useChat'
import { useTheme } from '../hooks/useTheme'

/**
 * The main page: wires the useChat hook's state/actions into the
 * presentational chat + itinerary components. No API calls or rendering
 * logic live here directly — this file only composes.
 *
 * Layout: chat and itinerary stack vertically on small screens (the page
 * itself scrolls) and sit side by side with independent scroll regions
 * from the `lg` breakpoint up — no fixed widths, just fluid flex sizing.
 */
export default function Home() {
  const { theme, setTheme } = useTheme()
  const {
    messages,
    isLoading,
    error,
    itinerary,
    meta,
    canRetry,
    sendMessage,
    retryLastMessage,
    resetConversation,
    clearError,
  } = useChat()

  // The composer's draft text is transient UI state, not conversation
  // state — it lives here (not useChat) so a suggestion-chip click can
  // populate it without useChat needing to know the input exists.
  const [draftMessage, setDraftMessage] = useState('')

  const handleSend = (text) => {
    sendMessage(text)
    setDraftMessage('')
  }

  const handleNewTrip = () => {
    resetConversation()
    setDraftMessage('')
    requestAnimationFrame(() => {
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' })
    })
  }

  return (
    <div className="app-shell bg-background flex min-h-screen flex-col lg:h-screen">
      <Header onNewTrip={handleNewTrip} hasConversation={messages.length > 0} />

      {error && (
        <div className="px-4 pt-4">
          <div className="mx-auto max-w-5xl">
            <ErrorMessage
              message={error}
              onDismiss={clearError}
              onRetry={canRetry ? retryLastMessage : undefined}
            />
          </div>
        </div>
      )}

      <div className="workspace flex min-h-0 flex-1 flex-col lg:flex-row lg:overflow-hidden">
        <div className="chat-visual-panel bg-surface flex min-w-0 flex-col lg:overflow-hidden">
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSuggestionClick={setDraftMessage}
          />
          <ChatInput
            value={draftMessage}
            onChange={setDraftMessage}
            onSend={handleSend}
            isLoading={isLoading}
          />
        </div>

        {itinerary && (
          <a href="#itinerary-results" className="mobile-results-jump">
            View itinerary
          </a>
        )}

        <div id="itinerary-results" className="results-panel border-border bg-background flex min-w-0 flex-col border-t lg:overflow-y-auto lg:border-t-0 lg:border-l">
          <ItineraryPanel itinerary={itinerary} isLoading={isLoading} meta={meta} theme={theme} onThemeChange={setTheme} />
        </div>
      </div>
    </div>
  )
}
