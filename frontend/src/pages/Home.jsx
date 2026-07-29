import Header from '../components/common/Header'
import ErrorMessage from '../components/common/ErrorMessage'
import ChatWindow from '../components/chat/ChatWindow'
import ChatInput from '../components/chat/ChatInput'
import { useChat } from '../hooks/useChat'

/**
 * The chat page: wires the useChat hook's state/actions into the
 * presentational chat components. No API calls or state logic live here
 * directly — this file only composes.
 */
export default function Home() {
  const { messages, isLoading, error, sendMessage, clearError } = useChat()

  return (
    <div className="flex h-screen flex-col bg-gray-100">
      <Header />

      {error && (
        <div className="px-4 pt-4">
          <div className="mx-auto max-w-2xl">
            <ErrorMessage message={error} onDismiss={clearError} />
          </div>
        </div>
      )}

      <ChatWindow messages={messages} isLoading={isLoading} />
      <ChatInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  )
}
