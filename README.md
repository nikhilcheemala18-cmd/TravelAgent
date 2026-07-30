# Flyo — AI Travel Booking Agent (Backend)

FastAPI backend for an AI *agent* (not a scripted chatbot) that plans and
executes travel-booking tool calls on behalf of a user.

For the React chat frontend, see [frontend/README.md](frontend/README.md).

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
- **ItineraryBuilder** and **ResponseBuilder** are real (Phase 6) — turn
  recovered tool results into a structured, frontend-ready `Itinerary` and
  a rich `ChatResponse`, handling partial results gracefully.
- Tools (`flight_search`, `hotel_search`, `car_rental_search`) still
  return mock data — the only remaining placeholder.

## Why "agent" and not "chatbot"

A chatbot maps input to a canned response. This system separates:

- **deciding what to do** (Planner — LLM-powered reasoning, never executes)
- **doing it** (Tool Executor + Tool implementations, via the Tool Registry)
- **checking the result is trustworthy** (Validator — never retries or executes)
- **handling it when it isn't** (Fallback Manager — retries transient
  failures through the ToolExecutor, never a tool directly)
- **presenting the outcome** (Itinerary Builder + Response Builder — never
  execute, retry, validate, or call an LLM)

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
│   ├── itinerary.py                  # Itinerary and its sections (business-level)
│   └── response.py                    # ExecutionSummary/ToolResultSummary/... (API envelope)
├── agent/                    # the agent's core components (one file each)
│   ├── conversation_manager.py    # session/message lifecycle + TravelSession state
│   ├── extraction.py               # SlotExtractor interface + LLM-backed implementation
│   ├── prompts/
│   │   └── extraction.py            # extraction system/user prompt templates
│   ├── planner.py                   # Planner interface + LLMPlanner
│   ├── tool_executor.py              # runs an ExecutionPlan against the ToolRegistry
│   ├── validator.py                   # Validator interface + DefaultValidator
│   ├── fallback_manager.py             # FallbackManager interface + retry-capable implementation
│   ├── itinerary_builder.py             # ItineraryBuilder interface + section-registry-driven builder
│   ├── response_builder.py               # ResponseBuilder — assembles the final ChatResponse
│   └── orchestrator.py                     # wires the above into one request flow
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
                                                                    ↓
                                                            ResponseBuilder
                                                                    ↓
                                                              ChatResponse
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
   `options` list. Produces a `ValidationResult` — it never retries,
   executes, or touches the plan/itinerary.
5. `FallbackManager` retries only tools with a transient `FailureReason`
   (never a missing tool or malformed data), up to `FALLBACK_MAX_RETRIES`
   times, by re-invoking `ToolExecutor.execute_step` — never a tool
   directly. Already-successful results are always preserved untouched.
   Returns a `FallbackOutcome` (`results`, `retry_attempts`,
   `unresolved_tools`, ...).
6. `ItineraryBuilder` takes `FallbackOutcome.results` + the `ValidationResult`
   + the `TravelSession` and builds a business-level `Itinerary`:
   `traveler_information`, `flight_options`/`hotel_options`/
   `car_rental_options`, a computed `trip_summary` (nights, estimated
   cost), simple `recommendations` (cheapest flight, best-rated hotel),
   `unavailable_services` for anything that never recovered, and
   `warnings`/`notices` — no raw tool arguments, timings, or retry
   mechanics leak into it. It runs unconditionally, so a total failure
   just produces an itinerary with everything under
   `unavailable_services` and `is_partial=True`, rather than the
   orchestrator special-casing that outcome.
7. `ResponseBuilder` wraps that `Itinerary` in the final `ChatResponse`,
   adding business-level `execution_summary`, `tool_results_summary`,
   `validation_summary`, and `fallback_summary` — again no internal
   details, just what a frontend needs to render a status view.
   `success` reflects whether the itinerary actually contains anything
   bookable, not merely whether every tool happened to succeed.
8. The reply is recorded in conversation history and `ChatResponse` is returned.

Failures never crash the pipeline: a broken `Planner` call and a broken
`ToolExecutor.execute_plan` call are each caught at the orchestrator level
and turned into a graceful `ChatResponse` via `FallbackManager` before
ever reaching `ItineraryBuilder`.

## ChatResponse shape

Every turn returns the same `ChatResponse` envelope; only the fields
relevant to that turn's outcome are populated:

| Field | Populated when |
|---|---|
| `reply`, `session_id` | always |
| `requires_clarification`, `missing_slots` | the Planner needs more trip details |
| `itinerary`, `execution_summary`, `tool_results_summary`, `validation_summary`, `fallback_summary`, `warnings`, `success` | the pipeline reached `ItineraryBuilder`/`ResponseBuilder` (whether that produced a full, partial, or empty itinerary) |

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
| `LLM_PROVIDER` | `mock` | Which `LLMClient` `app/llm/factory.py` builds: `mock` (offline, no credentials), `openai`, or `gemini`. |
| `LLM_API_KEY` | _(empty)_ | Required for `openai`/`gemini`. |
| `LLM_MODEL` | `gpt-4o-mini` | Model name passed to the provider — e.g. `gemini-flash-latest` for Gemini. Provider-specific; check what your API key currently has access to (model availability shifts over time, e.g. a specific dated model can be retired for new keys — a `-latest` alias avoids that). |
| `LLM_BASE_URL` | _(empty)_ | Optional override for OpenAI-compatible endpoints (e.g. a local Ollama server). Not used by `gemini`. |

To add a new provider (Claude, a local Ollama client, ...):
1. Add `app/llm/providers/<name>_client.py` implementing `LLMClient.complete`.
2. Register it in `app/llm/factory.py::_PROVIDER_FACTORIES`.
3. Set `LLM_PROVIDER=<name>` in `.env`.

`gemini` (`app/llm/providers/gemini_client.py`, via the `google-genai`
SDK) is implemented as a second worked example alongside `openai` —
useful as a reference when adding Claude or another provider.

Nothing in `app/agent/` changes — `Planner` and `LLMExtractor` only ever
depend on the `LLMClient` interface.

### Natural-language extraction

`LLMExtractor` (`app/agent/extraction.py`) anchors every extraction call
to the current date, so the prompt (`app/agent/prompts/extraction.py`)
can instruct the model to resolve relative expressions ("next Friday",
"tomorrow", "in two weeks") into absolute ISO 8601 dates instead of only
accepting fixed formats. The model is asked to always return all seven
`TravelSession` fields, `null` for anything not mentioned — the
`OpenAILLMClient` additionally requests JSON mode (`response_format`) as
a provider-side guarantee of syntactically valid JSON, entirely inside
that provider file. `MockLLMClient` (the default, offline) only
recognizes explicit ISO dates — resolving relative phrases needs a real
provider.

## Replacing mocks with real travel APIs

Everything mock-specific lives in `app/tools/*.py`. Each tool:

- implements `BaseTool.execute(tool_input) -> ToolOutput`
- is registered in `app/tools/registry.py::build_default_registry`

To integrate a real provider (flights, hotels, car rentals), replace the
body of the relevant tool's `execute` with a real API call — the
`*Input`/`*Output` Pydantic contracts in `app/schemas/tools.py`, and the
`ToolExecutionResult` envelope the executor wraps them in, are
provider-agnostic and shouldn't need to change for a typical REST API.
`Validator`, `FallbackManager`, and `ItineraryBuilder` don't change
either — they all work off the generic `ToolExecutionResult`/option-schema
contract, not anything mock-specific. Add provider credentials to
`app/config.py::Settings` and `.env`.

## Adding a new travel category (weather, attractions, visa info, ...)

`ItineraryBuilder` is registry-driven (`_SECTION_SPECS` in
`app/agent/itinerary_builder.py`), so adding a new searchable category
that follows the existing `options: list[...]` tool-output shape means:

1. Add the `ToolName`, a tool implementation, and register it in
   `app/tools/registry.py` (Phase 3 pattern).
2. Add its `*Option` schema to `app/schemas/tools.py`.
3. Add a matching `list[...Option]` field to `Itinerary` in
   `app/schemas/itinerary.py`.
4. Add one `_SectionSpec` entry in `app/agent/itinerary_builder.py`.

`Planner` also needs to plan the new tool's `ExecutionStep` — nothing else
in `ItineraryBuilder`/`ResponseBuilder`/`Validator`/`FallbackManager`
changes.

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
