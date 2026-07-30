# Flyo — Travel AI Agent Frontend

React (JavaScript, `.jsx`) interface for the Travel AI Agent backend, built
with Vite + Tailwind CSS + Axios.

- **F1** — chat interface: message bubbles, session persistence, error handling.
- **F2** — structured itinerary UI alongside the chat: trip summary, flight
  and hotel cards, recommendations, warnings, and unavailable-service
  notices, rendered from the backend's `ChatResponse.itinerary`.

Still not implemented (later phases): auth, dark mode, animations, maps,
provider logos, deployment.

## Project layout

```
src/
├── api/
│   └── travelApi.js          # Axios client — the one place the backend URL lives
├── components/
│   ├── chat/                  # ChatWindow, MessageBubble, ChatInput — presentational
│   ├── common/                 # Header, Loading, ErrorMessage — presentational
│   └── itinerary/                # Structured itinerary UI — presentational (see below)
├── hooks/
│   └── useChat.js             # Owns conversation + itinerary state: messages,
│                                  session_id, loading, error, latest itinerary
├── pages/
│   └── Home.jsx                # Composes Header + chat + ItineraryPanel via useChat
├── utils/
│   ├── formatTime.js           # Timestamp formatting for message bubbles
│   ├── errorMessages.js        # Axios error -> friendly user-facing message
│   ├── formatCurrency.js       # Intl-based amount + currency formatting
│   └── formatFieldLabel.js     # snake_case field name -> human label
├── styles/
│   └── index.css                # Tailwind entrypoint (`@import "tailwindcss"`)
├── App.jsx                       # Route wiring only (react-router-dom)
└── main.jsx                       # React root
```

### `components/itinerary/`

| Component | Renders |
|---|---|
| `ItineraryPanel.jsx` | Top-level composer: reads an `itinerary` object and renders each section below only if it has data; shows `EmptyItinerary` when there's none yet. |
| `TripSummaryCard.jsx` | `traveler_information` (origin, destination, dates, passengers, budget, hotel rating) + `trip_summary.total_estimated_cost`. |
| `FlightCard.jsx` / `HotelCard.jsx` | One card per option. Known fields get a dedicated layout; any *other* field the backend adds later still renders automatically via a generic label/value loop (`formatFieldLabel` + `InfoRow`) — no card change needed to support new API fields. |
| `RecommendationCard.jsx` | One backend recommendation string — kept visually and structurally separate from chat messages. |
| `WarningCard.jsx` | One warning or unavailable-service message (amber, `role="alert"`) — reused for both `itinerary.warnings` and `itinerary.unavailable_services`. |
| `SectionTitle.jsx` / `InfoRow.jsx` | Small shared primitives used across the cards above. |
| `EmptyItinerary.jsx` | Friendly placeholder shown before any itinerary exists. |

`services/` still exists for later phases and is intentionally empty.

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

## Conversation + itinerary flow

`useChat` (in `src/hooks/useChat.js`) sends each message to
`POST {VITE_API_BASE_URL}/chat` with the current `session_id` (`null` on
the first message), stores whatever `session_id` the backend returns, and
includes it on every subsequent call. Whenever a response includes a
non-null `itinerary`, the hook also updates its `itinerary` state — this
is preserved across later turns that don't include one (e.g. a follow-up
clarification question), so the itinerary panel doesn't flash empty
mid-conversation.

`Home.jsx` lays the two out side by side from the `lg` breakpoint up
(each pane independently scrollable) and stacked on smaller screens (the
page itself scrolls) — no fixed widths, purely fluid flex sizing.

## Error handling

`src/utils/errorMessages.js` maps three Axios failure shapes to a
friendly message:
- the backend responded with a non-2xx status (shows its `detail` if present)
- the request was sent but no response came back (network/CORS/backend down)
- anything else

Empty/whitespace-only messages are blocked client-side (the Send button
disables itself) before a request is ever made.
