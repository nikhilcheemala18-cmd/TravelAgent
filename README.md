# Flyo — AI Travel Booking Agent (Backend)

FastAPI backend for an AI *agent* (not a scripted chatbot) that plans and
executes travel-booking tool calls on behalf of a user. Business logic is
intentionally not implemented yet — this is the architectural skeleton:
interfaces, Pydantic contracts, and mock tool implementations.

## Why "agent" and not "chatbot"

A chatbot maps input to a canned response. This system separates:

- **deciding what to do** (Agent Planner)
- **doing it** (Tool Executor + Tool implementations)
- **checking the result is trustworthy** (Validator)
- **handling it when it isn't** (Fallback Manager)
- **presenting the outcome** (Itinerary Builder)

The Orchestrator sequences these steps; no single component knows the
whole flow except the orchestrator itself.

## Project layout

```
backend/app/
├── main.py                 # FastAPI app + router wiring
├── config.py                # env-driven settings (Settings/get_settings)
├── api/
│   ├── deps.py               # DI providers — swap implementations here
│   └── routes/
│       ├── chat.py            # POST /api/v1/chat
│       └── health.py          # GET  /api/v1/health
├── schemas/                 # Pydantic models (the contracts between layers)
│   ├── common.py              # shared enums
│   ├── conversation.py        # ChatRequest/ChatResponse/ConversationState
│   ├── agent.py                # AgentPlan/PlannedAction
│   ├── tools.py                 # per-tool Input/Output models + ToolCallResult
│   ├── validation.py            # ValidationResult/ValidationIssue
│   └── itinerary.py             # Itinerary
├── agent/                   # the agent's core components (one file each)
│   ├── conversation_manager.py   # session + message history
│   ├── planner.py                 # AgentPlanner interface + placeholder
│   ├── tool_executor.py            # runs a plan against the ToolRegistry
│   ├── validator.py                 # Validator interface + placeholder
│   ├── fallback_manager.py           # FallbackManager interface + placeholder
│   ├── itinerary_builder.py           # ItineraryBuilder interface + placeholder
│   └── orchestrator.py                 # wires the above into one request flow
├── tools/                    # tool implementations (mock today)
│   ├── base.py                 # BaseTool interface
│   ├── registry.py              # ToolName -> tool instance lookup
│   ├── flight_search.py
│   ├── hotel_search.py
│   └── car_rental.py
├── session/
│   └── store.py               # SessionStore interface + in-memory impl
└── utils/
    └── logging.py
```

## Request flow (`POST /api/v1/chat`)

1. `ConversationManager` loads/creates the session and records the user message.
2. `AgentPlanner` turns the message + conversation state into an `AgentPlan`
   (which tools to call, or a clarification question).
3. `ToolExecutor` runs each planned action against the `ToolRegistry`,
   producing `ToolCallResult`s.
4. `Validator` checks the results are usable.
5. On failure: `FallbackManager` produces a user-facing message.
   On success: `ItineraryBuilder` assembles an `Itinerary`.
6. `ChatResponse` is returned and the reply is recorded in conversation history.

## Replacing mocks with real travel APIs

Everything mock-specific lives in `app/tools/*.py`. Each tool:

- implements `BaseTool.execute(tool_input) -> ToolOutput`
- is registered in `app/tools/registry.py::build_default_registry`

To integrate a real provider (flights, hotels, car rentals), replace the
body of the relevant tool's `execute` with a real API call — the
`*Input`/`*Output` Pydantic contracts in `app/schemas/tools.py` are
provider-agnostic and shouldn't need to change for a typical REST API.
Add provider credentials to `app/config.py::Settings` and `.env`.

The `AgentPlanner`, `Validator`, `FallbackManager`, and `ItineraryBuilder`
placeholders in `app/agent/` are the other extension points — each is an
ABC with a single placeholder implementation, swappable independently via
`app/api/deps.py`.

## Running locally

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --app-dir .
```

Then `POST http://127.0.0.1:8000/api/v1/chat` with `{"message": "hi"}`.
