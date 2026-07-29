# Flyo — Travel AI Agent Frontend

React (JavaScript, `.jsx`) chat interface for the Travel AI Agent backend,
built with Vite + Tailwind CSS + Axios.

This phase (F1) implements the chat interface only — no itinerary/flight/
hotel cards, no auth, no dark mode, no animations. Those are later
frontend phases; today the assistant's replies render as plain text
message bubbles.

## Project layout

```
src/
├── api/
│   └── travelApi.js       # Axios client — the one place the backend URL lives
├── components/
│   ├── chat/               # ChatWindow, MessageBubble, ChatInput — presentational
│   └── common/               # Header, Loading, ErrorMessage — presentational
├── hooks/
│   └── useChat.js          # Owns conversation state: messages, session_id, loading, error
├── pages/
│   └── Home.jsx            # Composes Header + ChatWindow + ChatInput via useChat
├── utils/
│   ├── formatTime.js       # Timestamp formatting for message bubbles
│   └── errorMessages.js    # Axios error -> friendly user-facing message
├── styles/
│   └── index.css           # Tailwind entrypoint (`@import "tailwindcss"`)
├── App.jsx                  # Route wiring only (react-router-dom)
└── main.jsx                  # React root
```

`services/` and `components/itinerary/` exist for later phases and are
intentionally empty right now.

## Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

`.env` sets `VITE_API_BASE_URL` — the FastAPI backend's base URL
(including its `/api/v1` prefix). This is the only place the backend URL
is configured; nothing else in the app hardcodes it. Point it at wherever
the backend is running (see `../backend/README.md`).

## Conversation flow

`useChat` (in `src/hooks/useChat.js`) sends each message to
`POST {VITE_API_BASE_URL}/chat` with the current `session_id` (`null` on
the first message), stores whatever `session_id` the backend returns, and
includes it on every subsequent call — that's what makes multi-turn
conversation state work without any backend session cookie/auth.

## Error handling

`src/utils/errorMessages.js` maps three Axios failure shapes to a
friendly message:
- the backend responded with a non-2xx status (shows its `detail` if present)
- the request was sent but no response came back (network/CORS/backend down)
- anything else

Empty/whitespace-only messages are blocked client-side (the Send button
disables itself) before a request is ever made.
