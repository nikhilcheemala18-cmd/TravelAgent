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
 * backend session id, loading/error state, and the sendMessage action.
 * Keeping this in one hook (rather than spread across components) is
 * what lets ChatWindow/ChatInput stay presentational.
 */
export function useChat() {
  const [messages, setMessages] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

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

  return { messages, sessionId, isLoading, error, sendMessage, clearError }
}
