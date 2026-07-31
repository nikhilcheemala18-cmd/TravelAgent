"""Hotel search tool.

Mock implementation that simulates a realistic hotel-search API response:
a mixed set of budget, mid-range, and premium properties across different
hotel types, with varying amenities, review scores, and locations — enough
variation for downstream ranking/recommendation logic to have something
meaningful to choose between. It also behaves like a real API would for a
destination it doesn't serve or a search that matches nothing: it returns
success with an empty list and a conversational `empty_reason`, never a
fabricated result and never an exception. Swap the body of `execute` for
a real provider call (e.g. Booking.com, Expedia Rapid API) when ready —
the HotelSearchInput/Output contract (and the HotelOption fields) are
provider-agnostic and shouldn't need to change for a typical REST
provider.
"""

import random
from dataclasses import dataclass

from app.schemas.common import ToolName
from app.schemas.tools import HotelOption, HotelSearchInput, HotelSearchOutput, HotelType
from app.tools.base import BaseTool
from app.tools.mock_data import is_supported_destination, unsupported_destination_message

_HOTEL_NAMES: tuple[str, ...] = (
    "Grand Plaza Hotel",
    "Sunset Bay Resort",
    "Downtown Boutique Inn",
    "Harbor View Suites",
    "The Metropolitan",
    "Garden Terrace Hotel",
    "Skyline Residency",
    "Palm Grove Resort",
    "Central Square Hotel",
    "Riverside Inn",
    "Golden Sands Resort",
    "Urban Nest Hostel",
    "Comfort Stay Inn",
    "The Grand Continental",
    "Emerald Hills Hotel",
    "Silver Oak Guesthouse",
    "Lakeside Retreat",
    "The Wayfarer Hotel",
)

_LOCATIONS: tuple[str, ...] = (
    "City Center",
    "Downtown",
    "Beachfront",
    "Near Airport",
    "Historic District",
    "Business District",
    "Old Town",
    "Waterfront",
    "Uptown",
    "Suburban",
)

_AMENITY_POOL: tuple[str, ...] = (
    "Free WiFi",
    "Swimming Pool",
    "Fitness Center",
    "Free Breakfast",
    "Parking",
    "Spa & Wellness",
    "Airport Shuttle",
    "Pet Friendly",
    "Room Service",
    "Bar/Lounge",
    "Air Conditioning",
    "Business Center",
    "Laundry Service",
    "Restaurant On-site",
    "Rooftop Terrace",
)


@dataclass(frozen=True)
class _PriceTier:
    star_rating_range: tuple[float, float]
    price_range: tuple[float, float]
    review_score_range: tuple[float, float]
    amenity_count_range: tuple[int, int]
    hotel_types: tuple[HotelType, ...]


_BUDGET = _PriceTier(
    star_rating_range=(2.0, 3.0),
    price_range=(40.0, 90.0),
    review_score_range=(6.0, 7.8),
    amenity_count_range=(2, 4),
    hotel_types=(HotelType.HOSTEL, HotelType.GUESTHOUSE, HotelType.HOTEL),
)
_MID_RANGE = _PriceTier(
    star_rating_range=(3.0, 4.0),
    price_range=(90.0, 200.0),
    review_score_range=(7.2, 8.8),
    amenity_count_range=(4, 7),
    hotel_types=(HotelType.HOTEL, HotelType.BOUTIQUE, HotelType.APARTMENT),
)
_PREMIUM = _PriceTier(
    star_rating_range=(4.0, 5.0),
    price_range=(200.0, 500.0),
    review_score_range=(8.3, 9.8),
    amenity_count_range=(6, 10),
    hotel_types=(HotelType.HOTEL, HotelType.RESORT, HotelType.BOUTIQUE),
)
# Index-matched to the first three generated hotels so every result set
# is guaranteed at least one of each tier, rather than leaving "budget,
# mid-range, and premium options" up to random chance.
_GUARANTEED_TIERS: tuple[_PriceTier, ...] = (_BUDGET, _MID_RANGE, _PREMIUM)

_MIN_OPTIONS = 10
_MAX_OPTIONS = 15


class HotelSearchTool(BaseTool):
    name = ToolName.HOTEL_SEARCH

    def execute(self, tool_input: HotelSearchInput) -> HotelSearchOutput:
        # TODO: replace with a real hotel provider API call.
        parsed = HotelSearchInput.model_validate(tool_input)

        if not is_supported_destination(parsed.destination):
            return HotelSearchOutput(
                success=True, options=[], empty_reason=unsupported_destination_message()
            )

        count = random.randint(_MIN_OPTIONS, _MAX_OPTIONS)
        names = random.sample(_HOTEL_NAMES, k=min(count, len(_HOTEL_NAMES)))
        # Only relevant if _MAX_OPTIONS ever exceeds the name pool size —
        # fall back to repeats rather than raising.
        while len(names) < count:
            names.append(random.choice(_HOTEL_NAMES))

        options = [
            self._generate_option(name, self._pick_tier(index))
            for index, name in enumerate(names)
        ]

        if parsed.min_rating is not None:
            options = [option for option in options if option.star_rating >= parsed.min_rating]
            if not options:
                return HotelSearchOutput(
                    success=True,
                    options=[],
                    empty_reason=(
                        f"I couldn't find any hotels rated {parsed.min_rating:g} stars or higher. "
                        "Try lowering your rating preference."
                    ),
                )

        options.sort(key=lambda option: option.price_per_night)
        return HotelSearchOutput(success=True, options=options)

    @staticmethod
    def _pick_tier(index: int) -> _PriceTier:
        if index < len(_GUARANTEED_TIERS):
            return _GUARANTEED_TIERS[index]
        return random.choice(_GUARANTEED_TIERS)

    @staticmethod
    def _generate_option(name: str, tier: _PriceTier) -> HotelOption:
        amenity_count = random.randint(*tier.amenity_count_range)
        amenities = random.sample(_AMENITY_POOL, k=amenity_count)

        return HotelOption(
            name=name,
            star_rating=round(random.uniform(*tier.star_rating_range), 1),
            price_per_night=round(random.uniform(*tier.price_range), 2),
            amenities=amenities,
            location=random.choice(_LOCATIONS),
            review_score=round(random.uniform(*tier.review_score_range), 1),
            hotel_type=random.choice(tier.hotel_types),
        )
