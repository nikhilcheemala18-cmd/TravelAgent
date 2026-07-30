import { useCallback, useState } from 'react'
import { sendChatMessage } from '../api/travelApi'
import { getFriendlyErrorMessage } from '../utils/errorMessages'

let messageIdCounter = 0
function nextMessageId() {
  messageIdCounter += 1
  return `msg-${Date.now()}-${messageIdCounter}`
}

/**
 * Owns the conversation state for the chat UI: message history, the
 * backend session id, loading/error state, the latest structured
 * itinerary, and the sendMessage action. Keeping this in one hook (rather
 * than spread across components) is what lets ChatWindow/ChatInput/
 * ItineraryPanel all stay presentational.
 */
export function useChat() {
  const [messages, setMessages] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  // Most recent non-null itinerary the backend has returned. Kept even
  // when a later turn is a clarification question with no itinerary of
  // its own, so the panel doesn't flash empty mid-refinement.
  const [itinerary, setItinerary] = useState(null)

  const clearError = useCallback(() => setError(null), [])

  const sendMessage = useCallback(
    async (rawText) => {
      const text = rawText.trim()
      if (!text) {
        setError('Please enter a message before sending.')
        return
      }

      setError(null)
      setMessages((prev) => [
        ...prev,
        { id: nextMessageId(), role: 'user', content: text, timestamp: new Date().toISOString() },
      ])
      setIsLoading(true)

      try {
        // The backend issues a session_id on the first call and expects
        // it echoed back on every subsequent call for this conversation.
        const data = await sendChatMessage(text, sessionId)
        setSessionId(data.session_id)
        if (data.itinerary) {
          setItinerary(data.itinerary)
        }
        setMessages((prev) => [
          ...prev,
          {
            id: nextMessageId(),
            role: 'assistant',
            content: data.reply,
            timestamp: new Date().toISOString(),
          },
        ])
      } catch (err) {
        setError(getFriendlyErrorMessage(err))
      } finally {
        setIsLoading(false)
      }
    },
    [sessionId],
  )

  return { messages, sessionId, isLoading, error, itinerary, sendMessage, clearError }
}
