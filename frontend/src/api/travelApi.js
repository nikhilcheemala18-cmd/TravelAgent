

import axios from 'axios'

const API_PREFIX = '/api/v1'
const DEFAULT_BACKEND_URL = 'http://127.0.0.1:8000'

function normalizeBackendUrl(url) {
  const withoutTrailingSlash = url.replace(/\/+$/, '')
  return withoutTrailingSlash.endsWith(API_PREFIX)
    ? withoutTrailingSlash.slice(0, -API_PREFIX.length)
    : withoutTrailingSlash
}

const BACKEND_URL = normalizeBackendUrl(
  import.meta.env.VITE_API_BASE_URL || DEFAULT_BACKEND_URL,
)

const apiClient = axios.create({
  baseURL: `${BACKEND_URL}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

/**
 * Send a chat message to the AI Travel Assistant.
 *
 * @param {string} message - User message.
 * @param {string|null} sessionId - Current conversation session ID.
 * @returns {Promise<object>} ChatResponse from the backend.
 */
export async function sendChatMessage(message, sessionId) {
  const response = await apiClient.post('/chat', {
    message,
    session_id: sessionId ?? null,
  })

  return response.data
}

/**
 * Optional health check helper.
 * Useful for verifying backend connectivity.
 */
export async function checkHealth() {
  const response = await apiClient.get('/health')
  return response.data
}

export default apiClient
