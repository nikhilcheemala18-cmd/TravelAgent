import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import Loading from '../common/Loading'

/**
 * Scrollable message list. Purely presentational — conversation state
 * lives in the useChat hook and is passed in as props.
 */
export default function ChatWindow({ messages, isLoading }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: 'end' })
  }, [messages, isLoading])

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="mx-auto flex max-w-2xl flex-col gap-3">
        {messages.length === 0 && !isLoading && (
          <p className="text-center text-sm text-gray-400">
            Start planning your trip — tell me where you&apos;d like to go.
          </p>
        )}

        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
          />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-4 py-2 shadow-sm">
              <Loading />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
