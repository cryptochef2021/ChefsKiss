from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.review import Review
from app.models.host import Host
from app.models.platform import Platform
from app.schemas.review import HostReviewSummary, ReviewResponse


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def get_host_summary(self, host_id: int) -> HostReviewSummary:
        host = self.db.query(Host).filter(Host.id == host_id).first()
        if not host:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Host not found")

        # Count reviews per platform
        platform_counts = (
            self.db.query(Platform.name, func.count(Review.id))
            .join(Review, Review.platform_id == Platform.id)
            .filter(Review.host_id == host_id)
            .group_by(Platform.name)
            .all()
        )

        # Get recent reviews
        recent = (
            self.db.query(Review)
            .join(Platform)
            .filter(Review.host_id == host_id)
            .order_by(Review.review_date.desc().nullslast())
            .limit(10)
            .all()
        )

        return HostReviewSummary(
            host_id=host.id,
            host_name=host.name,
            aggregate_rating=host.aggregate_rating,
            total_reviews=host.total_reviews,
            reviews_by_platform={name: count for name, count in platform_counts},
            recent_reviews=[
                ReviewResponse(
                    id=r.id,
                    platform_name=r.platform.display_name if r.platform else None,
                    reviewer_name=r.reviewer_name,
                    rating=r.rating,
                    text=r.text,
                    text_translated=r.text_translated,
                    review_date=r.review_date,
                )
                for r in recent
            ],
        )
