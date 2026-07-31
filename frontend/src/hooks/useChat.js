import { useCallback, useRef, useState } from 'react'
import { sendChatMessage } from '../api/travelApi'
import { getFriendlyErrorMessage } from '../utils/errorMessages'

let messageIdCounter = 0
function nextMessageId() {
  messageIdCounter += 1
  return `msg-${Date.now()}-${messageIdCounter}`
}

const initialMeta = {
  executionSummary: null,
  toolResultsSummary: null,
  validationSummary: null,
  fallbackSummary: null,
}

/**
 * Owns the conversation state for the chat UI: message history, the
 * backend session id, loading/error state, the latest structured
 * itinerary + execution metadata, and the send/retry/reset actions.
 * Keeping this in one hook (rather than spread across components) is
 * what lets ChatWindow/ChatInput/ItineraryPanel all stay presentational.
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
  const [meta, setMeta] = useState(initialMeta)
  const [canRetry, setCanRetry] = useState(false)

  // Refs mirror the latest session id / last-failed message so
  // `sendMessage` can stay a single stable callback (no stale-closure
  // risk) while `isSendingRef` guards against a second send landing
  // before React has re-rendered with isLoading=true.
  const sessionIdRef = useRef(null)
  const lastFailedMessageRef = useRef(null)
  const isSendingRef = useRef(false)

  const clearError = useCallback(() => setError(null), [])

  const sendMessage = useCallback(async (rawText) => {
    const text = rawText.trim()
    if (!text) {
      setError('Please enter a message before sending.')
      return
    }
    if (isSendingRef.current) return
    isSendingRef.current = true

    setError(null)
    lastFailedMessageRef.current = null
    setCanRetry(false)
    setMessages((prev) => [
      ...prev,
      { id: nextMessageId(), role: 'user', content: text, timestamp: new Date().toISOString() },
    ])
    setIsLoading(true)

    try {
      // The backend issues a session_id on the first call and expects
      // it echoed back on every subsequent call for this conversation.
      const data = await sendChatMessage(text, sessionIdRef.current)

      if (!data || typeof data.reply !== 'string' || typeof data.session_id !== 'string') {
        throw new Error('invalid_response')
      }

      sessionIdRef.current = data.session_id
      setSessionId(data.session_id)
      if (data.itinerary) {
        setItinerary(data.itinerary)
      }
      setMeta({
        executionSummary: data.execution_summary ?? null,
        toolResultsSummary: data.tool_results_summary ?? null,
        validationSummary: data.validation_summary ?? null,
        fallbackSummary: data.fallback_summary ?? null,
      })
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
      lastFailedMessageRef.current = text
      setCanRetry(true)
      setError(
        err instanceof Error && err.message === 'invalid_response'
          ? 'Received an unexpected response from the server. Please try again.'
          : getFriendlyErrorMessage(err),
      )
      // Drop the optimistic user bubble tied to the failed send so a
      // retry doesn't leave a duplicate once it succeeds.
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
      isSendingRef.current = false
    }
  }, [])

  const retryLastMessage = useCallback(() => {
    if (lastFailedMessageRef.current) {
      sendMessage(lastFailedMessageRef.current)
    }
  }, [sendMessage])

  const resetConversation = useCallback(() => {
    isSendingRef.current = false
    lastFailedMessageRef.current = null
    sessionIdRef.current = null
    setMessages([])
    setSessionId(null)
    setItinerary(null)
    setMeta(initialMeta)
    setCanRetry(false)
    setError(null)
    setIsLoading(false)
  }, [])

  return {
    messages,
    sessionId,
    isLoading,
    error,
    itinerary,
    meta,
    canRetry,
    sendMessage,
    retryLastMessage,
    resetConversation,
    clearError,
  }
}
