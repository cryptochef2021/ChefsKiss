import pytest
from datetime import datetime, timezone
from fastapi import HTTPException

from app.models.review import Review
from app.services.review_service import ReviewService


class TestReviewService:
    def _seed_reviews(self, db_session):
        reviews = [
            Review(
                host_id=1,
                platform_id=1,
                reviewer_name="Alice",
                rating=5.0,
                text="Amazing place!",
                review_date=datetime(2026, 1, 15, tzinfo=timezone.utc),
            ),
            Review(
                host_id=1,
                platform_id=1,
                reviewer_name="Bob",
                rating=4.0,
                text="Good location",
                review_date=datetime(2026, 1, 10, tzinfo=timezone.utc),
            ),
            Review(
                host_id=1,
                platform_id=2,
                reviewer_name="Charlie",
                rating=4.5,
                text="Clean and comfortable",
                review_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
            ),
        ]
        for r in reviews:
            db_session.add(r)
        db_session.commit()

    def test_get_host_summary(self, db_session):
        self._seed_reviews(db_session)
        service = ReviewService(db_session)
        summary = service.get_host_summary(1)

        assert summary.host_id == 1
        assert summary.host_name == "Test Host"
        assert summary.aggregate_rating == 4.5
        assert summary.total_reviews == 10

    def test_get_host_summary_reviews_by_platform(self, db_session):
        self._seed_reviews(db_session)
        service = ReviewService(db_session)
        summary = service.get_host_summary(1)

        assert summary.reviews_by_platform["airbnb"] == 2
        assert summary.reviews_by_platform["agoda"] == 1

    def test_get_host_summary_recent_reviews(self, db_session):
        self._seed_reviews(db_session)
        service = ReviewService(db_session)
        summary = service.get_host_summary(1)

        assert len(summary.recent_reviews) == 3
        # Should be sorted by date descending
        assert summary.recent_reviews[0].reviewer_name == "Charlie"

    def test_get_host_summary_not_found(self, db_session):
        service = ReviewService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            service.get_host_summary(999)
        assert exc_info.value.status_code == 404
