import { Info, Plane, Hotel, Sparkles, TriangleAlert } from 'lucide-react'
import SectionTitle from './SectionTitle'
import TripSummaryCard from './TripSummaryCard'
import FlightCard from './FlightCard'
import HotelCard from './HotelCard'
import RecommendationCard from './RecommendationCard'
import WarningCard from './WarningCard'
import EmptyItinerary from './EmptyItinerary'
import ExecutionSummaryPanel from './ExecutionSummaryPanel'
import Loading from '../common/Loading'
import ThemeToggle from '../common/ThemeToggle'
import { useProgressiveLoadingMessage } from '../../hooks/useProgressiveLoadingMessage'
import { getFlightBadges } from '../../utils/flightBadges'

/**
 * Composes the structured itinerary sections from a ChatResponse's
 * `itinerary` (+ optional `meta` execution/validation/fallback summaries).
 * Every section is conditionally rendered — only sections with actual
 * data take up space. Pure presentation: all the data comes in as props,
 * nothing here calls the API or owns conversation state.
 */
export default function ItineraryPanel({ itinerary, isLoading, meta, theme, onThemeChange }) {
  const loadingLabel = useProgressiveLoadingMessage(isLoading)
  const unavailableMessages = (itinerary?.unavailable_services ?? []).map(
    (service) => `${service.service}: ${service.reason}`,
  )
  const flightBadges = getFlightBadges(itinerary?.flight_options ?? [])

  return (
    <div className="flex min-h-full flex-col">
      <div className="itinerary-toolbar px-4 sm:px-6">
        <div className="demo-disclosure inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs">
          <Info className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          Demo Mode - Simulated Travel Inventory
        </div>
        <ThemeToggle theme={theme} onThemeChange={onThemeChange} />
      </div>
      {isLoading && (
        <div className="border-border bg-card border-b px-4 py-3 sm:px-6">
          <Loading label={loadingLabel} />
        </div>
      )}

      {!itinerary ? (
        <EmptyItinerary />
      ) : (
        <div className="flex flex-col gap-5 p-4 sm:p-5">
          <TripSummaryCard
            travelerInfo={itinerary.traveler_information}
            tripSummary={itinerary.trip_summary}
          />

          {itinerary.flight_options?.length > 0 && (
            <section>
              <SectionTitle icon={Plane} meta={`${itinerary.flight_options.length} options`}>Flights</SectionTitle>
              <div className="flex flex-col gap-3">
                {itinerary.flight_options.map((flight, index) => (
                  <FlightCard
                    key={flight.flight_number ?? index}
                    flight={flight}
                    badges={flightBadges[index]}
                  />
                ))}
              </div>
            </section>
          )}

          {itinerary.hotel_options?.length > 0 && (
            <section>
              <SectionTitle icon={Hotel} meta={`${itinerary.hotel_options.length} options`}>Hotels</SectionTitle>
              <div className="flex flex-col gap-3">
                {itinerary.hotel_options.map((hotel, index) => (
                  <HotelCard key={hotel.name ?? index} hotel={hotel} />
                ))}
              </div>
            </section>
          )}

          {itinerary.recommendations?.length > 0 && (
            <section>
              <SectionTitle icon={Sparkles}>Recommendations</SectionTitle>
              <div className="flex flex-col gap-2">
                {itinerary.recommendations.map((text, index) => (
                  <RecommendationCard key={index} text={text} />
                ))}
              </div>
            </section>
          )}

          {itinerary.warnings?.length > 0 && (
            <section>
              <SectionTitle icon={TriangleAlert}>Warnings</SectionTitle>
              <div className="flex flex-col gap-2">
                {itinerary.warnings.map((text, index) => (
                  <WarningCard key={index} text={text} />
                ))}
              </div>
            </section>
          )}

          {unavailableMessages.length > 0 && (
            <section>
              <SectionTitle icon={TriangleAlert}>Unavailable Services</SectionTitle>
              <div className="flex flex-col gap-2">
                {unavailableMessages.map((text, index) => (
                  <WarningCard key={index} text={text} />
                ))}
              </div>
            </section>
          )}

          <ExecutionSummaryPanel
            executionSummary={meta?.executionSummary}
            toolResultsSummary={meta?.toolResultsSummary}
            validationSummary={meta?.validationSummary}
            fallbackSummary={meta?.fallbackSummary}
          />
        </div>
      )}
    </div>
  )
}
