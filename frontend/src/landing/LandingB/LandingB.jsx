import { Link } from 'react-router-dom'
import { ArrowRight, CalendarDays, MapPin, MessageSquareText, Plane, Search } from 'lucide-react'
import TravelMark from '../../components/common/TravelMark'
import mediterraneanImage from '../../assets/travel-chat-mediterranean.jpg'

const GLASS_STEPS = [
  ['01', 'Describe the trip'],
  ['02', 'Confirm details'],
  ['03', 'Shape the itinerary'],
]

export default function LandingB() {
  return (
    <main className="landing landing-b">
      <section className="landing-b-hero" aria-label="Flyo liquid glass landing page">
        <div className="landing-b-video" aria-hidden="true">
          <img src={mediterraneanImage} alt="" />
        </div>
        <div className="landing-b-whitewash" aria-hidden="true" />

        <nav className="landing-nav landing-nav-dark" aria-label="Landing navigation">
          <Link to="/" className="landing-brand" aria-label="Flyo landing page">
            <TravelMark />
            <span>FLYO</span>
          </Link>
          <div className="landing-nav-links" aria-label="Page sections">
            <a href="#how-b">01 / HOW IT WORKS</a>
            <a href="#features-b">02 / FEATURES</a>
            <a href="#technology-b">03 / TECHNOLOGY</a>
          </div>
          <Link to="/workspace" className="landing-nav-cta landing-nav-cta-dark">
            TRY WORKSPACE
          </Link>
        </nav>

        <div className="landing-b-center">
          <p className="landing-kicker">FLYO</p>
          <h1>Where will you go next?</h1>
          <p>
            Tell Flyo where you are going and what you love. We will create a personalized travel plan
            through conversation, using simulated flights and stays for transparent planning.
          </p>

          <form className="landing-glass-card" aria-label="Example Flyo prompt" onSubmit={(event) => event.preventDefault()}>
            <div className="landing-glass-prompt">
              <MessageSquareText aria-hidden="true" />
              <span>
                "I'm planning a 7-day trip to Japan in October. I love food, hidden cafes,
                scenic hikes, and want to avoid crowds."
              </span>
            </div>
            <Link to="/workspace" className="landing-glass-button">
              Plan My Trip
              <ArrowRight aria-hidden="true" />
            </Link>
          </form>
        </div>
      </section>

      <section id="how-b" className="landing-section landing-section-glass">
        <div className="landing-section-heading landing-section-heading-centered">
          <p>HOW IT WORKS</p>
          <h2>One prompt, then a clearer plan.</h2>
        </div>
        <div className="landing-b-steps">
          {GLASS_STEPS.map(([number, label]) => (
            <article key={number}>
              <span>{number}</span>
              <h3>{label}</h3>
            </article>
          ))}
        </div>
      </section>

      <section id="features-b" className="landing-b-editorial">
        <div>
          <p>CONVERSATIONAL PLANNING</p>
          <h2>Designed for the messy middle of planning.</h2>
        </div>
        <div className="landing-b-panel">
          <div className="landing-b-panel-row">
            <Search aria-hidden="true" />
            <span>Hyderabad to Bangaluru next Friday</span>
          </div>
          <div className="landing-b-panel-row active">
            <MapPin aria-hidden="true" />
            <span>Did you mean Bengaluru?</span>
          </div>
          <div className="landing-b-panel-row">
            <CalendarDays aria-hidden="true" />
            <span>Dates and travellers confirmed</span>
          </div>
          <div className="landing-b-panel-row">
            <Plane aria-hidden="true" />
            <span>Simulated options ready</span>
          </div>
        </div>
      </section>

      <section id="technology-b" className="landing-b-footer-strip">
        <span>Structured extraction</span>
        <span>City normalization</span>
        <span>Simulated travel inventory</span>
        <Link to="/workspace">Try Workspace</Link>
      </section>
    </main>
  )
}
