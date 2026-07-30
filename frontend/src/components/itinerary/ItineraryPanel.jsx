import SectionTitle from './SectionTitle'
import TripSummaryCard from './TripSummaryCard'
import FlightCard from './FlightCard'
import HotelCard from './HotelCard'
import RecommendationCard from './RecommendationCard'
import WarningCard from './WarningCard'
import EmptyItinerary from './EmptyItinerary'
import Loading from '../common/Loading'

/**
 * Composes the structured itinerary sections from a ChatResponse's
 * `itinerary` object. Every section is conditionally rendered — only
 * sections with actual data take up space. Pure presentation: all the
 * data comes in as props, nothing here calls the API or owns state.
 */
export default function ItineraryPanel({ itinerary, isLoading }) {
  const unavailableMessages = (itinerary?.unavailable_services ?? []).map(
    (service) => `${service.service}: ${service.reason}`,
  )

  return (
    <div className="flex h-full flex-col">
      {isLoading && (
        <div className="border-b border-gray-200 bg-white px-4 py-3 sm:px-6">
          <Loading label="Updating your itinerary..." />
        </div>
      )}

      {!itinerary ? (
        <EmptyItinerary />
      ) : (
        <div className="flex flex-col gap-6 p-4 sm:p-6">
          <TripSummaryCard
            travelerInfo={itinerary.traveler_information}
            tripSummary={itinerary.trip_summary}
          />

          {itinerary.flight_options?.length > 0 && (
            <section>
              <SectionTitle>Flights</SectionTitle>
              <div className="flex flex-col gap-3">
                {itinerary.flight_options.map((flight, index) => (
                  <FlightCard key={flight.flight_number ?? index} flight={flight} />
                ))}
              </div>
            </section>
          )}

          {itinerary.hotel_options?.length > 0 && (
            <section>
              <SectionTitle>Hotels</SectionTitle>
              <div className="flex flex-col gap-3">
                {itinerary.hotel_options.map((hotel, index) => (
                  <HotelCard key={hotel.name ?? index} hotel={hotel} />
                ))}
              </div>
            </section>
          )}

          {itinerary.recommendations?.length > 0 && (
            <section>
              <SectionTitle>Recommendations</SectionTitle>
              <div className="flex flex-col gap-2">
                {itinerary.recommendations.map((text, index) => (
                  <RecommendationCard key={index} text={text} />
                ))}
              </div>
            </section>
          )}

          {itinerary.warnings?.length > 0 && (
            <section>
              <SectionTitle>Warnings</SectionTitle>
              <div className="flex flex-col gap-2">
                {itinerary.warnings.map((text, index) => (
                  <WarningCard key={index} text={text} />
                ))}
              </div>
            </section>
          )}

          {unavailableMessages.length > 0 && (
            <section>
              <SectionTitle>Unavailable Services</SectionTitle>
              <div className="flex flex-col gap-2">
                {unavailableMessages.map((text, index) => (
                  <WarningCard key={index} text={text} />
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  )
}
