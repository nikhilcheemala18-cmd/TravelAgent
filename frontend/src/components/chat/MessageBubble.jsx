import { formatTimestamp } from '../../utils/formatTime'

export default function MessageBubble({ role, content, timestamp }) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm shadow-sm ${
          isUser
            ? 'rounded-br-sm bg-blue-600 text-white'
            : 'rounded-bl-sm border border-gray-200 bg-white text-gray-900'
        }`}
      >
        <p className="whitespace-pre-wrap break-words">{content}</p>
        {timestamp && (
          <span className={`mt-1 block text-[11px] ${isUser ? 'text-blue-100' : 'text-gray-400'}`}>
            {formatTimestamp(timestamp)}
          </span>
        )}
      </div>
    </div>
  )
}
