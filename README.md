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
- **Validator** and **FallbackManager** are real (Phase 5) — structured
  result verification, transient-failure classification, and bounded
  retry-based recovery.
- **ItineraryBuilder** is still a placeholder (flattens everything
  verbatim), and tools (`flight_search`, `hotel_search`,
  `car_rental_search`) still return mock data.

## Why "agent" and not "chatbot"

A chatbot maps input to a canned response. This system separates:

- **deciding what to do** (Planner — LLM-powered reasoning, never executes)
- **doing it** (Tool Executor + Tool implementations, via the Tool Registry)
- **checking the result is trustworthy** (Validator — never retries or executes)
- **handling it when it isn't** (Fallback Manager — retries transient
  failures through the ToolExecutor, never a tool directly)
- **presenting the outcome** (Itinerary Builder)

The Orchestrator sequences these steps; no single component knows the
whole flow except the orchestrator itself, and each stage only ever sees
the previous stage's output. The LLM only ever produces structured JSON
for the Planner to reason over — it never calls a tool or an external API
directly.

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
│   ├── validation.py               # ValidationResult/ValidatedToolResult/FailureReason
│   ├── fallback.py                  # FallbackOutcome/RetryAttempt
│   └── itinerary.py                  # Itinerary
├── agent/                    # the agent's core components (one file each)
│   ├── conversation_manager.py    # session/message lifecycle + TravelSession state
│   ├── extraction.py               # SlotExtractor interface + LLM-backed implementation
│   ├── prompts/
│   │   └── extraction.py            # extraction system/user prompt templates
│   ├── planner.py                   # Planner interface + LLMPlanner
│   ├── tool_executor.py              # runs an ExecutionPlan against the ToolRegistry
│   ├── validator.py                   # Validator interface + DefaultValidator
│   ├── fallback_manager.py             # FallbackManager interface + retry-capable implementation
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
                          ↑                                        ↓
                    SlotExtractor → LLMClient           ToolExecutionResult
                    (provider-agnostic)                            ↓
                                                                Validator
                                                                    ↓
                                                            FallbackManager
                                                                    ↓
                                                            ItineraryBuilder
```

1. `ConversationManager` loads/creates the session and records the user message.
2. `Planner` asks its `SlotExtractor` to pull trip details out of the
   message (an `LLMClient` call under the hood), merges them into the
   session via `ConversationManager`, and returns either a
   `ClarificationAction` (missing required slots — with a follow-up
   question) or an `ExecutionPlan` (ordered `ExecutionStep`s). The LLM
   only reasons and returns structured JSON; it never touches a tool.
3. `ToolExecutor` runs each step of the `ExecutionPlan` in priority order
   via the `ToolRegistry` (no if/elif dispatch), returning one
   `ToolExecutionResult` per step.
4. `Validator` checks every result: did the tool fail (and why —
   `FailureReason`: missing tool, timeout, execution failure), and if it
   succeeded, does `returned_data` have a well-formed, non-empty
   `options` list. Produces a `ValidationResult` (`overall_status`,
   `failed_tools`, `warnings`, `validated_results`) — it never retries,
   executes, or touches the plan/itinerary.
5. `FallbackManager` receives that `ValidationResult`. If nothing failed,
   results pass through untouched. If something failed, it retries only
   the tools whose failure looks transient (`execution_failed`/`timeout`
   — never a missing tool or malformed data), up to `FALLBACK_MAX_RETRIES`
   times with `FALLBACK_RETRY_DELAY_MS` between attempts, by re-invoking
   `ToolExecutor.execute_step` (never a tool directly). Already-successful
   results are always preserved untouched. Returns a `FallbackOutcome`
   (`resolved`, `results`, `retry_attempts`, `unresolved_tools`, `message`).
6. If `FallbackOutcome.resolved` is `False` (nothing usable survived),
   the orchestrator returns `FallbackOutcome.message` directly and skips
   `ItineraryBuilder`. Otherwise `ItineraryBuilder` builds an `Itinerary`
   from `FallbackOutcome.results` (which may be a partial set — a tool
   that couldn't be recovered is simply absent, not fatal).
7. `ChatResponse` is returned and the reply is recorded in conversation history.

Failures never crash the pipeline: a broken `Planner` call, a broken
`ToolExecutor.execute_plan` call, and an unrecoverable `FallbackOutcome`
are each caught at the orchestrator level and turned into a graceful
`ChatResponse` via `FallbackManager`.

## Retry / fallback configuration

| Variable | Default | Purpose |
|---|---|---|
| `FALLBACK_MAX_RETRIES` | `2` | Max retry attempts per transiently-failed tool. `0` disables retries (failures are still reported, just never retried). |
| `FALLBACK_RETRY_DELAY_MS` | `250` | Delay before each retry attempt. |

Retries are bounded (never infinite), scoped only to the specific tools
that failed with a transient `FailureReason`, and isolated entirely inside
`FallbackManager` — `ToolExecutor` itself has no retry logic and is
unaware retries happen.

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
`Validator` and `FallbackManager` don't change either: they already work
off the generic `ToolExecutionResult`/option-schema contract, not
anything mock-specific. Add provider credentials to
`app/config.py::Settings` and `.env`.

`ItineraryBuilder` is the remaining placeholder extension point — an ABC
with a single placeholder implementation, swappable via `app/api/deps.py`.

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
