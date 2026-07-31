import { formatTimestamp } from '../../utils/formatTime'

export default function MessageBubble({ role, content, timestamp }) {
  const isUser = role === 'user'

  return (
    <div className={`animate-message-in flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`shadow-card max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
          isUser
            ? 'bg-primary rounded-br-sm text-white'
            : 'border-border bg-card text-ink rounded-bl-sm border'
        }`}
      >
        <p className="whitespace-pre-wrap break-words">{content}</p>
        {timestamp && (
          // A literal Text Secondary gray reads poorly against the primary
          // blue user bubble, so it keeps a light tint there instead —
          // same role (de-emphasized timestamp), adapted for contrast.
          <span className={`mt-1 block text-[11px] ${isUser ? 'text-white/70' : 'text-ink-muted'}`}>
            {formatTimestamp(timestamp)}
          </span>
        )}
      </div>
    </div>
  )
}
