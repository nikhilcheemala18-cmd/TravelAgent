export default function ErrorMessage({ message, onDismiss }) {
  if (!message) return null

  return (
    <div
      role="alert"
      className="flex items-start justify-between gap-3 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      <span>{message}</span>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 font-medium text-red-700 hover:text-red-900"
          aria-label="Dismiss error"
        >
          Dismiss
        </button>
      )}
    </div>
  )
}
