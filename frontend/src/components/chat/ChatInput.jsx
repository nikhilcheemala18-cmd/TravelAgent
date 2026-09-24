import { Send } from 'lucide-react'

/**
 * Message composer. Controlled by the parent (`value`/`onChange`) so a
 * welcome-screen suggestion click can populate it. Submits on button
 * click or Enter (Shift+Enter for a newline); disabled while a request
 * is in flight or the field is empty.
 */
export default function ChatInput({ value, onChange, onSend, isLoading }) {
  const handleSubmit = (event) => {
    event.preventDefault()
    if (!value.trim() || isLoading) return
    onSend(value)
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit(event)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="chat-composer">
      <div className="composer-inner mx-auto flex items-end gap-3">
        <textarea
          aria-label="Your travel request"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Tell me about your trip..."
          disabled={isLoading}
          className="composer-input text-ink placeholder:text-ink-muted focus:ring-primary/20 min-w-0 flex-1 resize-none transition focus:ring-2 focus:outline-none"
        />
        <button
          type="submit"
          disabled={isLoading || !value.trim()}
          className="send-button bg-action hover:bg-action-hover inline-flex items-center justify-center gap-2 text-sm font-medium text-white transition active:scale-95 disabled:cursor-not-allowed disabled:active:scale-100"
        >
          <Send className="h-4 w-4" aria-hidden="true" />
          Send
        </button>
      </div>
    </form>
  )
}
