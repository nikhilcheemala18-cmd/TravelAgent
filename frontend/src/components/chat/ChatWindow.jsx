import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import WelcomeScreen from './WelcomeScreen'
import Loading from '../common/Loading'
import AssistantAvatar from './AssistantAvatar'

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
      <div className="chat-scroll flex min-h-0 flex-1 flex-col overflow-y-auto">
        <WelcomeScreen onSuggestionClick={onSuggestionClick} />
      </div>
    )
  }

  return (
    <div className="chat-scroll min-h-0 flex-1 overflow-y-auto" role="log" aria-label="Travel conversation" aria-live="polite">
      <div className="conversation-content mx-auto flex flex-col">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
          />
        ))}

        {isLoading && (
          <div className="message-row animate-message-in flex justify-start">
            <AssistantAvatar />
            <div className="border-border bg-card shadow-card rounded-2xl rounded-bl-sm border px-4 py-3">
              <Loading label="Processing your trip request" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
