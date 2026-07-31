import { useState } from 'react'
import Header from '../components/common/Header'
import ErrorMessage from '../components/common/ErrorMessage'
import ChatWindow from '../components/chat/ChatWindow'
import ChatInput from '../components/chat/ChatInput'
import ItineraryPanel from '../components/itinerary/ItineraryPanel'
import { useChat } from '../hooks/useChat'

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
  }

  return (
    <div className="bg-background flex min-h-screen flex-col lg:h-screen">
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

      <div className="flex flex-1 flex-col lg:flex-row lg:overflow-hidden">
        <div className="bg-surface flex flex-col lg:flex-1 lg:overflow-hidden">
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

        <div className="border-border bg-background flex flex-col border-t lg:flex-1 lg:overflow-y-auto lg:border-t-0 lg:border-l">
          <ItineraryPanel itinerary={itinerary} isLoading={isLoading} meta={meta} />
        </div>
      </div>
    </div>
  )
}
