from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.review import HostReviewSummary
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/host/{host_id}", response_model=HostReviewSummary)
def get_host_reviews(host_id: int, db: Session = Depends(get_db)):
    """Get aggregated reviews for a host across all platforms."""
    service = ReviewService(db)
    return service.get_host_summary(host_id)
