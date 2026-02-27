from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/listing/{listing_id}/availability")
def get_availability(listing_id: int, db: Session = Depends(get_db)):
    """Get unified availability calendar for a listing (merged from all iCal sources)."""
    service = CalendarService(db)
    return service.get_availability(listing_id)


@router.post("/listing/{listing_id}/sync")
def sync_calendar(listing_id: int, db: Session = Depends(get_db)):
    """Trigger an iCal sync for a listing."""
    service = CalendarService(db)
    return service.sync(listing_id)
