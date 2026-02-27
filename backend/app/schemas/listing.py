from pydantic import BaseModel
from datetime import datetime


class ListingBase(BaseModel):
    title: str
    city: str
    country: str
    price_per_night: float | None = None
    price_per_month: float | None = None
    currency: str = "USD"
    property_type: str | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    max_guests: int | None = None


class ListingResponse(ListingBase):
    id: int
    platform_name: str | None = None
    host_name: str | None = None
    title_translated: str | None = None
    description_translated: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    listing_url: str
    rating: float | None = None
    review_count: int = 0
    aggregate_host_rating: float | None = None
    total_host_reviews: int = 0
    scraped_at: datetime | None = None

    class Config:
        from_attributes = True


class ListingSearchParams(BaseModel):
    city: str | None = None
    country: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    price_type: str = "monthly"  # "nightly" or "monthly"
    property_type: str | None = None
    min_bedrooms: int | None = None
    platforms: list[str] | None = None
    sort_by: str = "price"  # "price", "rating", "reviews"
    page: int = 1
    page_size: int = 20
