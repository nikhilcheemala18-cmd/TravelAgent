/**
 * Friendly, sanitized error banner. `message` should already be a
 * user-facing string (see src/utils/errorMessages.js) — this component
 * never touches raw error/exception details itself.
 */
export default function ErrorMessage({ message, onDismiss, onRetry }) {
  if (!message) return null

  return (
    <div
      role="alert"
      className="animate-fade-in border-error/30 bg-error/10 text-error flex items-start justify-between gap-3 rounded-lg border px-4 py-3 text-sm"
    >
      <span>{message}</span>
      <div className="flex shrink-0 items-center gap-3">
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="text-error decoration-error/40 font-medium underline underline-offset-2 transition hover:opacity-80"
          >
            Retry
          </button>
        )}
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            aria-label="Dismiss error"
            className="text-error font-medium transition hover:opacity-80"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  )
}
