# Flyo — AI Travel Booking Agent (Backend)

FastAPI backend for an AI *agent* (not a scripted chatbot) that plans and
executes travel-booking tool calls on behalf of a user.

Implemented so far:
- **ConversationManager** is real (Phase 2) — session state, slot
  merging, completeness checks.
- **Planner** is real and LLM-powered (Phase 2 + Phase 4) — delegates
  language understanding to an injected `SlotExtractor`/`LLMClient`;
  provider is config-driven (`LLM_PROVIDER`, defaults to a fully offline
  mock).
- **ToolExecutor** and **ToolRegistry** are real (Phase 3) — registry-based
  tool dispatch, priority-ordered execution, per-step timing.
- **Validator**, **FallbackManager**, and **ItineraryBuilder** are still
  placeholders (pass-through / flatten-everything), and tools
  (`flight_search`, `hotel_search`, `car_rental_search`) still return mock
  data — these are the next phases.

## Why "agent" and not "chatbot"

A chatbot maps input to a canned response. This system separates:

- **deciding what to do** (Planner — LLM-powered reasoning, never executes)
- **doing it** (Tool Executor + Tool implementations, via the Tool Registry)
- **checking the result is trustworthy** (Validator)
- **handling it when it isn't** (Fallback Manager)
- **presenting the outcome** (Itinerary Builder)

The Orchestrator sequences these steps; no single component knows the
whole flow except the orchestrator itself. The LLM only ever produces
structured JSON for the Planner to reason over — it never calls a tool or
an external API directly.

## Project layout

```
backend/app/
├── main.py                  # FastAPI app + router wiring
├── config.py                 # env-driven settings (Settings/get_settings)
├── api/
│   ├── deps.py                # DI providers — swap implementations here
│   └── routes/
│       ├── chat.py             # POST /api/v1/chat
│       └── health.py           # GET  /api/v1/health
├── schemas/                  # Pydantic models (the contracts between layers)
│   ├── common.py               # shared enums (ToolName, ActionStatus, ...)
│   ├── conversation.py         # ChatRequest/ChatResponse/ConversationState
│   ├── travel_session.py       # TravelSession — the trip slot state
│   ├── agent.py                 # ExecutionStep/ExecutionPlan/ClarificationAction
│   ├── tools.py                  # per-tool *Input/*Output models
│   ├── tool_execution.py          # ToolExecutionResult (ToolExecutor's output)
│   ├── validation.py               # ValidationResult/ValidationIssue
│   └── itinerary.py                 # Itinerary
├── agent/                    # the agent's core components (one file each)
│   ├── conversation_manager.py    # session/message lifecycle + TravelSession state
│   ├── extraction.py               # SlotExtractor interface + LLM-backed implementation
│   ├── prompts/
│   │   └── extraction.py            # extraction system/user prompt templates
│   ├── planner.py                   # Planner interface + LLMPlanner
│   ├── tool_executor.py              # runs an ExecutionPlan against the ToolRegistry
│   ├── validator.py                   # Validator interface + placeholder
│   ├── fallback_manager.py             # FallbackManager interface + placeholder
│   ├── itinerary_builder.py             # ItineraryBuilder interface + placeholder
│   └── orchestrator.py                   # wires the above into one request flow
├── llm/                       # LLM provider abstraction (Phase 4)
│   ├── base.py                  # LLMClient interface — the only thing callers depend on
│   ├── factory.py                 # LLM_PROVIDER -> LLMClient, the one place providers are chosen
│   └── providers/
│       ├── mock_client.py           # offline stand-in, default provider
│       └── openai_client.py          # OpenAI (or OpenAI-compatible) client
├── tools/                     # tool implementations (mock today)
│   ├── base.py                  # BaseTool interface
│   ├── registry.py               # ToolRegistry: register(tool) / get_tool(name)
│   ├── flight_search.py
│   ├── hotel_search.py
│   └── car_rental.py
├── session/
│   └── store.py                # SessionStore interface + in-memory impl
└── utils/
    └── logging.py
```

## Request flow (`POST /api/v1/chat`)

```
ConversationManager → Planner → ExecutionPlan → ToolExecutor → ToolRegistry → Tools
                          ↑
                    SlotExtractor → LLMClient (provider-agnostic)
```

1. `ConversationManager` loads/creates the session and records the user message.
2. `Planner` asks its `SlotExtractor` to pull trip details out of the
   message (an `LLMClient` call under the hood — see below), merges them
   into the session via `ConversationManager`, and returns either a
   `ClarificationAction` (missing required slots — with a follow-up
   question) or an `ExecutionPlan` (ordered `ExecutionStep`s). The LLM
   only reasons and returns structured JSON; it never touches a tool.
3. `ToolExecutor` runs each step of the `ExecutionPlan` in priority order,
   looking each tool up in the `ToolRegistry` (no if/elif dispatch), and
   returns a `ToolExecutionResult` per step (status, arguments, returned
   data, execution time).
4. `Validator` checks the results are usable.
5. On failure: `FallbackManager` produces a user-facing message.
   On success: `ItineraryBuilder` assembles an `Itinerary`.
6. `ChatResponse` is returned and the reply is recorded in conversation history.

If the LLM's extraction response is malformed (not JSON, not an object, or
fails `TravelSession` validation), `LLMSlotExtractor` raises
`SlotExtractionError` rather than guessing — the Planner doesn't catch it,
so it surfaces through the orchestrator's existing planning-failure path
(logged, then turned into a graceful reply by the unchanged
`FallbackManager`). No retries are attempted.

## LLM provider configuration

Set via `.env` / environment variables, read in `app/config.py::Settings`:

| Variable | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER` | `mock` | Which `LLMClient` `app/llm/factory.py` builds. `mock` needs no credentials and runs fully offline. |
| `LLM_API_KEY` | _(empty)_ | Required when `LLM_PROVIDER=openai`. |
| `LLM_MODEL` | `gpt-4o-mini` | Model name passed to the provider. |
| `LLM_BASE_URL` | _(empty)_ | Optional override for OpenAI-compatible endpoints (e.g. a local Ollama server). |

To add a new provider (Gemini, Claude, a local Ollama client, ...):
1. Add `app/llm/providers/<name>_client.py` implementing `LLMClient.complete`.
2. Register it in `app/llm/factory.py::_PROVIDER_FACTORIES`.
3. Set `LLM_PROVIDER=<name>` in `.env`.

Nothing in `app/agent/` changes — `Planner` and `LLMSlotExtractor` only ever
depend on the `LLMClient` interface.

## Replacing mocks with real travel APIs

Everything mock-specific lives in `app/tools/*.py`. Each tool:

- implements `BaseTool.execute(tool_input) -> ToolOutput`
- is registered in `app/tools/registry.py::build_default_registry`

To integrate a real provider (flights, hotels, car rentals), replace the
body of the relevant tool's `execute` with a real API call — the
`*Input`/`*Output` Pydantic contracts in `app/schemas/tools.py`, and the
`ToolExecutionResult` envelope the executor wraps them in, are
provider-agnostic and shouldn't need to change for a typical REST API.
Add provider credentials to `app/config.py::Settings` and `.env`.

The `Validator`, `FallbackManager`, and `ItineraryBuilder` placeholders in
`app/agent/` are the remaining extension points — each is an ABC with a
single placeholder implementation, swappable independently via
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
Works out of the box with `LLM_PROVIDER=mock` (the `.env.example`
default) — no API key needed.
