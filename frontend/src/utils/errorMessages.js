/**
 * Turn an Axios error into a short, user-facing message. Kept separate
 * from the chat hook so any future API call (not just chat) can reuse the
 * same network/backend-error handling.
 */
export function getFriendlyErrorMessage(error) {
  if (error?.response) {
    // The backend responded, but with a non-2xx status.
    const detail = error.response.data?.detail
    if (typeof detail === 'string') return detail
    return `The server returned an error (status ${error.response.status}). Please try again.`
  }

  if (error?.request) {
    // The request was sent but no response came back (network/CORS/offline).
    return 'Unable to reach the server. Please check your connection and try again.'
  }

  return 'Something went wrong. Please try again.'
}
