from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ScrapedListing:
    external_id: str
    title: str
    description: str | None
    city: str
    country: str
    address: str | None
    latitude: float | None
    longitude: float | None
    price_per_night: float | None
    price_per_month: float | None
    currency: str
    property_type: str | None
    bedrooms: int | None
    bathrooms: int | None
    max_guests: int | None
    listing_url: str
    image_urls: list[str]
    host_name: str | None
    rating: float | None
    review_count: int
    original_language: str | None
    ical_url: str | None = None


class BaseScraper(ABC):
    """Base class for all platform scrapers."""

    platform_name: str

    @abstractmethod
    async def search(self, city: str, country: str, **kwargs) -> list[ScrapedListing]:
        """Search for listings on this platform."""
        ...

    @abstractmethod
    async def get_listing(self, external_id: str) -> ScrapedListing | None:
        """Get a single listing by its platform-specific ID."""
        ...

    @abstractmethod
    async def get_reviews(self, external_id: str) -> list[dict]:
        """Get reviews for a listing."""
        ...
