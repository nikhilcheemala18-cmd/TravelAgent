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
  const { messages, isLoading, error, itinerary, sendMessage, clearError } = useChat()

  return (
    <div className="flex min-h-screen flex-col bg-gray-100 lg:h-screen">
      <Header />

      {error && (
        <div className="px-4 pt-4">
          <div className="mx-auto max-w-5xl">
            <ErrorMessage message={error} onDismiss={clearError} />
          </div>
        </div>
      )}

      <div className="flex flex-1 flex-col lg:flex-row lg:overflow-hidden">
        <div className="flex flex-col lg:flex-1 lg:overflow-hidden">
          <ChatWindow messages={messages} isLoading={isLoading} />
          <ChatInput onSend={sendMessage} isLoading={isLoading} />
        </div>

        <div className="flex flex-col border-t border-gray-200 lg:flex-1 lg:overflow-y-auto lg:border-t-0 lg:border-l">
          <ItineraryPanel itinerary={itinerary} isLoading={isLoading} />
        </div>
      </div>
    </div>
  )
}
