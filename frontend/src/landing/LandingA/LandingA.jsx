import { Link } from 'react-router-dom'
import {
  ArrowRight,
  CheckCircle2,
  Code2,
  Database,
  Layers,
  Plane,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'
import TravelMark from '../../components/common/TravelMark'
import coastImage from '../../assets/travel-chat-coast.jpg'

const ARCHITECTURE_STAGES = [
  {
    number: '01',
    title: 'USER MESSAGE',
    copy: 'Natural-language travel request',
  },
  {
    number: '02',
    title: 'CONVERSATION MANAGER',
    copy: 'Maintains session-level travel state',
  },
  {
    number: '03',
    title: 'LLM PLANNER',
    copy: 'Determines the next planning action',
  },
  {
    number: '04',
    title: 'LLM EXTRACTOR',
    copy: 'Converts travel language into structured fields',
  },
  {
    number: '05',
    title: 'CITY RESOLUTION',
    copy: 'Normalizes aliases and confirms likely typos',
  },
  {
    number: '06',
    title: 'EXECUTION PLAN',
    copy: 'Represents supported operations to execute',
  },
  {
    number: '07',
    title: 'TOOL REGISTRY',
    copy: 'Resolves available travel capabilities',
  },
  {
    number: '08',
    title: 'VALIDATOR',
    copy: 'Checks returned results before itinerary construction',
  },
  {
    number: '09',
    title: 'FALLBACK MANAGER',
    copy: 'Handles incomplete, unsupported, or empty cases',
  },
  {
    number: '10',
    title: 'ITINERARY BUILDER',
    copy: 'Combines validated results into a structured trip',
  },
  {
    number: '11',
    title: 'RESPONSE BUILDER',
    copy: 'Produces the conversational response',
  },
]

const ENGINEERING_MODULES = [
  {
    number: '01',
    title: 'STRUCTURED LLM OUTPUT',
    description:
      'Travel requests are converted into structured fields such as origin, destination, dates, passengers, budget, and hotel preferences before planning begins.',
    visual: 'structured',
  },
  {
    number: '02',
    title: 'DETERMINISTIC CITY RESOLUTION',
    description:
      'LLM extraction is followed by deterministic city resolution so common aliases and likely typos do not unnecessarily break the conversation.',
    visual: 'city',
  },
  {
    number: '03',
    title: 'REGISTRY-BASED TOOL EXECUTION',
    description:
      'Travel capabilities are exposed through a registry-based tool layer, keeping orchestration separate from individual travel-service implementations.',
    visual: 'registry',
  },
  {
    number: '04',
    title: 'VALIDATION + BOUNDED FALLBACK',
    description:
      'Tool results are validated before itinerary construction, with bounded fallback behavior for incomplete, unsupported, or empty requests.',
    visual: 'fallback',
  },
]

const CONVERSATION_STEPS = [
  ['USER', '"Hyderabad to Bangalore next Friday for 2 people."'],
  ['FLYO', '"Did you mean Bengaluru (Bangalore)?"'],
  ['USER', '"Yes."'],
  ['FLYO', '"Great. I\'ll look for flights and hotels from Hyderabad to Bengaluru for next Friday for 2 people."'],
  ['USER', '"Actually make it 3-star hotels."'],
  ['FLYO', '"Got it. I\'ll update the hotel search to 3-star options."'],
]

const EVALUATION_METRICS = [
  ['97.2%', 'SCRIPTED WORKFLOW SUCCESS', '35 / 36 controlled HTTP scenarios'],
  ['100%', 'CORRECTION HANDLING', '20 / 20 scenarios'],
  ['90.9%', 'STRUCTURED FIELD EXTRACTION', '130 / 143 field comparisons'],
  ['88.6%', 'COMPLETE-RECORD EXTRACTION', '31 / 35 complete records'],
  ['2.18s', 'HTTP P95 LATENCY', '45 localhost API requests using real OpenAI calls'],
]

export default function LandingA() {
  return (
    <main className="landing landing-a">
      <section className="landing-a-hero" aria-label="Flyo cinematic landing page">
        <img src={coastImage} alt="" className="landing-a-hero-image" aria-hidden="true" />
        <div className="landing-a-atmosphere" aria-hidden="true" />

        <nav className="landing-nav landing-nav-light" aria-label="Landing navigation">
          <Link to="/" className="landing-brand" aria-label="Flyo landing page">
            <TravelMark />
            <span>FLYO</span>
          </Link>
          <div className="landing-nav-links" aria-label="Page sections">
            <a href="#how-a">01 / HOW IT WORKS</a>
            <a href="#features-a">02 / FEATURES</a>
            <a href="#technology-a">03 / TECHNOLOGY</a>
          </div>
          <Link to="/workspace" className="landing-nav-cta">
            TRY WORKSPACE
          </Link>
        </nav>

        <div className="landing-a-content">
          <p className="landing-kicker">AI travel planning agent</p>
          <h1>FLYO</h1>
          <h2>Your next journey starts with a conversation.</h2>
          <p>
            Tell Flyo where you are going, when you are travelling, and what matters to you.
            Flyo turns your conversation into a structured travel plan using simulated travel inventory.
          </p>
          <div className="landing-actions">
            <Link to="/workspace" className="landing-primary landing-primary-warm">
              Try Workspace
              <ArrowRight aria-hidden="true" />
            </Link>
            <a href="#how-a" className="landing-secondary landing-secondary-light">
              Explore how it works
            </a>
          </div>
        </div>

        <aside className="landing-a-preview" aria-label="Flyo trip planning preview">
          <div className="landing-a-preview-top">
            <span>Live planning shape</span>
            <Sparkles aria-hidden="true" />
          </div>
          <div className="landing-a-route">
            <span>HYD</span>
            <Plane aria-hidden="true" />
            <span>BLR</span>
          </div>
          <div className="landing-a-preview-grid">
            <div>
              <strong>2</strong>
              <span>travellers</span>
            </div>
            <div>
              <strong>Next Fri</strong>
              <span>departure</span>
            </div>
          </div>
          <p>Bengaluru confirmed. Simulated flights, stays, and itinerary blocks are ready to compare.</p>
        </aside>
      </section>

      <section id="how-a" className="case-section case-architecture">
        <div className="case-heading">
          <p>01 / AGENT ARCHITECTURE</p>
          <h2>From natural language to a structured travel plan.</h2>
          <span>
            Flyo uses a staged LLM planning pipeline to extract travel intent, resolve entities,
            plan supported tool execution, validate results, and construct an itinerary.
          </span>
        </div>

        <div className="architecture-diagram" aria-label="Flyo staged LLM planning pipeline">
          {ARCHITECTURE_STAGES.map((stage) => (
            <article key={stage.number} className="architecture-node">
              <span>{stage.number}</span>
              <h3>{stage.title}</h3>
              <p>{stage.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="features-a" className="case-section case-engineering">
        <div className="case-heading case-heading-split">
          <div>
            <p>02 / ENGINEERING</p>
            <h2>Designed as a pipeline, not a prompt.</h2>
          </div>
          <span>
            Flyo separates language interpretation, entity resolution, tool execution, validation,
            and itinerary construction so the system behaves like engineered software instead of a single prompt.
          </span>
        </div>

        <div className="engineering-grid">
          {ENGINEERING_MODULES.map((module) => (
            <article key={module.number} className={`engineering-module module-${module.visual}`}>
              <div className="module-copy">
                <span>{module.number}</span>
                <h3>{module.title}</h3>
                <p>{module.description}</p>
              </div>
              <ModuleVisual type={module.visual} />
            </article>
          ))}
        </div>
      </section>

      <section className="case-section case-conversation">
        <div className="case-heading">
          <p>03 / CONVERSATION</p>
          <h2>Travel plans rarely arrive perfectly formed.</h2>
          <span>
            Flyo is designed to refine a trip through conversation rather than requiring every constraint
            in the first message.
          </span>
        </div>

        <div className="conversation-system">
          <div className="conversation-sequence" aria-label="Flyo multi-turn correction example">
            {CONVERSATION_STEPS.map(([speaker, message]) => (
              <article key={`${speaker}-${message}`} className={speaker === 'FLYO' ? 'conversation-bubble flyo' : 'conversation-bubble'}>
                <span>{speaker}</span>
                <p>{message}</p>
              </article>
            ))}
          </div>
          <aside className="trip-state" aria-label="Trip state after conversation refinements">
            <p>TRIP STATE</p>
            <dl>
              <div>
                <dt>Origin</dt>
                <dd>Hyderabad</dd>
              </div>
              <div>
                <dt>Destination</dt>
                <dd>Bengaluru</dd>
              </div>
              <div>
                <dt>Departure</dt>
                <dd>Next Friday</dd>
              </div>
              <div>
                <dt>Passengers</dt>
                <dd>2</dd>
              </div>
              <div>
                <dt>Hotel</dt>
                <dd>3-star</dd>
              </div>
            </dl>
          </aside>
        </div>
      </section>

      <section className="case-section case-evaluation">
        <div className="case-heading case-heading-split">
          <div>
            <p>04 / EVALUATION</p>
            <h2>Measured against controlled travel scenarios.</h2>
          </div>
          <span>
            Evaluation performed against controlled HTTP scenarios using OpenAI gpt-4o-mini with simulated travel tools.
          </span>
        </div>

        <div className="metrics-grid">
          {EVALUATION_METRICS.map(([value, label, detail]) => (
            <article key={label} className="metric-card">
              <strong>{value}</strong>
              <span>{label}</span>
              <p>{detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="technology-a" className="case-section case-technology">
        <div className="case-heading">
          <p>05 / TECHNOLOGY</p>
          <h2>A full-stack AI system built for experimentation.</h2>
        </div>

        <div className="stack-layout">
          <div className="stack-diagram" aria-label="Flyo technology stack">
            <div className="stack-root">FLYO</div>
            <div className="stack-split">
              <article>
                <Code2 aria-hidden="true" />
                <h3>FRONTEND</h3>
                <p>React + Vite</p>
              </article>
              <article>
                <Database aria-hidden="true" />
                <h3>BACKEND</h3>
                <p>FastAPI</p>
              </article>
            </div>
            <div className="stack-chain">
              <span>Agent Orchestrator</span>
              <span>Conversation Manager</span>
              <span>LLM Abstraction</span>
              <div className="stack-branch">
                <span>OpenAI</span>
                <span>Gemini</span>
              </div>
              <span>Structured Schemas</span>
              <span>Tool Registry</span>
              <span>Travel Services</span>
              <span>Itinerary Builder</span>
            </div>
          </div>

          <div className="technology-list">
            <article>
              <span>FRONTEND</span>
              <p>React · Vite</p>
            </article>
            <article>
              <span>BACKEND</span>
              <p>Python · FastAPI</p>
            </article>
            <article>
              <span>AI</span>
              <p>OpenAI · Gemini · Structured LLM extraction</p>
            </article>
            <article>
              <span>ENGINEERING</span>
              <p>Pydantic · Session State · Tool Registry · Validation · Fallbacks</p>
            </article>
          </div>
        </div>
      </section>

      <section className="case-section case-product">
        <div className="case-heading">
          <p>06 / TRY THE SYSTEM</p>
          <h2>Enough architecture. Try the agent.</h2>
          <span>
            Start a conversation and see how Flyo turns travel requirements into a structured itinerary.
          </span>
        </div>

        <div className="product-cta-layout">
          <Link to="/workspace" className="case-primary-link">
            Open Workspace
            <ArrowRight aria-hidden="true" />
          </Link>
          <div className="workspace-preview" aria-label="Actual Flyo workspace preview">
            <div className="workspace-preview-header">
              <span>flyo</span>
              <small>Travel Assistant</small>
            </div>
            <div className="workspace-preview-body">
              <div className="workspace-chat">
                <p className="user-line">Hyderabad to Bangalore next Friday for 2 people.</p>
                <p className="assistant-line">Did you mean Bengaluru (Bangalore)?</p>
                <p className="user-line">Yes.</p>
                <p className="assistant-line">Found 9 flight option(s), 13 hotel option(s) for Bengaluru.</p>
              </div>
              <div className="workspace-result">
                <span>Trip Summary</span>
                <dl>
                  <div>
                    <dt>Origin</dt>
                    <dd>Hyderabad</dd>
                  </div>
                  <div>
                    <dt>Destination</dt>
                    <dd>Bengaluru</dd>
                  </div>
                  <div>
                    <dt>Inventory</dt>
                    <dd>Simulated</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

function ModuleVisual({ type }) {
  if (type === 'structured') {
    return (
      <div className="module-visual structured-visual" aria-label="Natural language to structured travel slots">
        <span>Natural language</span>
        <i />
        <span>LLM extraction</span>
        <i />
        <span>Structured travel slots</span>
        <i />
        <span>Validation</span>
        <pre>{`{
  origin: "Hyderabad",
  destination: "Bengaluru",
  passengers: 2,
  departure_date: "..."
}`}</pre>
      </div>
    )
  }

  if (type === 'city') {
    return (
      <div className="module-visual city-visual" aria-label="Bangalore alias and Bangaluru typo confirmation">
        <div>
          <span>Bangalore</span>
          <i />
          <strong>Bengaluru</strong>
          <i />
          <em>continue planning</em>
        </div>
        <div>
          <span>Bangaluru</span>
          <i />
          <strong>Did you mean Bengaluru?</strong>
          <i />
          <em>Yes → continue planning</em>
        </div>
        <p>Canonicalization is based on the supported travel inventory.</p>
      </div>
    )
  }

  if (type === 'registry') {
    return (
      <div className="module-visual registry-visual" aria-label="Tool registry connecting to travel capabilities">
        <div className="registry-root">
          <Layers aria-hidden="true" />
          <span>TOOL REGISTRY</span>
        </div>
        <div className="registry-tools">
          <span>FLIGHTS</span>
          <span>HOTELS</span>
          <span>CAR RENTAL</span>
        </div>
        <p>Travel inventory is simulated for this portfolio demonstration.</p>
      </div>
    )
  }

  return (
    <div className="module-visual fallback-visual" aria-label="Validation and bounded fallback">
      <span>Tool Results</span>
      <i />
      <strong>VALIDATOR</strong>
      <div className="fallback-split">
        <div>
          <CheckCircle2 aria-hidden="true" />
          <span>Valid</span>
          <em>Itinerary</em>
        </div>
        <div>
          <ShieldCheck aria-hidden="true" />
          <span>Invalid</span>
          <em>Fallback / Clarification</em>
        </div>
      </div>
    </div>
  )
}
