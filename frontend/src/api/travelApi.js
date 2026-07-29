/**
 * Reusable Axios client for the Travel AI Agent backend.
 *
 * This is the single place the backend URL and endpoint paths are
 * defined — nothing else in the app should hardcode a URL. Swapping
 * environments (local, staging, prod) is a `.env` change, not a code
 * change (see .env.example -> VITE_API_BASE_URL).
 */
import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

/**
 * Send a chat message to the agent.
 *
 * @param {string} message - The user's message text.
 * @param {string|null} sessionId - The current session id, or null on the
 *   very first message of a conversation.
 * @returns {Promise<object>} The backend's ChatResponse payload.
 */
export async function sendChatMessage(message, sessionId) {
  const response = await apiClient.post('/chat', {
    message,
    session_id: sessionId ?? null,
  })
  return response.data
}

export default apiClient
