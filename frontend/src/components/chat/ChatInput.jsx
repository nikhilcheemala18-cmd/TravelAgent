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
    <form onSubmit={handleSubmit} className="border-border bg-card border-t px-4 py-4">
      <div className="mx-auto flex max-w-2xl items-end gap-3">
        <textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Tell me about your trip..."
          disabled={isLoading}
          className="border-border bg-card text-ink placeholder:text-ink-muted focus:border-primary focus:ring-primary/20 disabled:bg-surface max-h-32 flex-1 resize-none rounded-xl border px-4 py-2.5 text-sm transition focus:ring-4 focus:outline-none"
        />
        <button
          type="submit"
          disabled={isLoading || !value.trim()}
          className="bg-primary hover:bg-primary-hover disabled:bg-border disabled:text-ink-muted rounded-xl px-4 py-2.5 text-sm font-medium text-white transition active:scale-95 disabled:cursor-not-allowed disabled:active:scale-100"
        >
          Send
        </button>
      </div>
    </form>
  )
}
