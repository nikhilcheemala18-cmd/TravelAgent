import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import WelcomeScreen from './WelcomeScreen'
import Loading from '../common/Loading'

/**
 * Scrollable message list, or the welcome screen before the first
 * message. Purely presentational — conversation state lives in the
 * useChat hook and is passed in as props.
 */
export default function ChatWindow({ messages, isLoading, onSuggestionClick }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: 'end', behavior: 'smooth' })
  }, [messages, isLoading])

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col overflow-y-auto">
        <WelcomeScreen onSuggestionClick={onSuggestionClick} />
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="mx-auto flex max-w-2xl flex-col gap-3">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
          />
        ))}

        {isLoading && (
          <div className="animate-message-in flex justify-start">
            <div className="border-border bg-card shadow-card rounded-2xl rounded-bl-sm border px-4 py-2.5">
              <Loading label="Assistant is typing" visibleLabel={false} />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
