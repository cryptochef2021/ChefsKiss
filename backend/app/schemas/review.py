from pydantic import BaseModel
from datetime import datetime


class ReviewResponse(BaseModel):
    id: int
    platform_name: str | None = None
    reviewer_name: str | None = None
    rating: float
    text: str | None = None
    text_translated: str | None = None
    review_date: datetime | None = None

    class Config:
        from_attributes = True


class HostReviewSummary(BaseModel):
    host_id: int
    host_name: str
    aggregate_rating: float | None = None
    total_reviews: int = 0
    reviews_by_platform: dict[str, int] = {}
    recent_reviews: list[ReviewResponse] = []
