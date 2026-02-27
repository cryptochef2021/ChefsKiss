from datetime import date

import httpx
from icalendar import Calendar
from sqlalchemy.orm import Session

from app.models.calendar_event import CalendarEvent
from app.models.listing import Listing


class CalendarService:
    def __init__(self, db: Session):
        self.db = db

    def get_availability(self, listing_id: int) -> dict:
        events = (
            self.db.query(CalendarEvent)
            .filter(CalendarEvent.listing_id == listing_id)
            .filter(CalendarEvent.end_date >= date.today())
            .order_by(CalendarEvent.start_date)
            .all()
        )

        return {
            "listing_id": listing_id,
            "blocked_dates": [
                {
                    "start": event.start_date.isoformat(),
                    "end": event.end_date.isoformat(),
                    "summary": event.summary,
                    "source": event.source_platform,
                }
                for event in events
            ],
        }

    def sync(self, listing_id: int) -> dict:
        listing = self.db.query(Listing).filter(Listing.id == listing_id).first()
        if not listing or not listing.ical_url:
            return {"status": "error", "message": "No iCal URL configured"}

        try:
            response = httpx.get(listing.ical_url, timeout=30)
            response.raise_for_status()
            cal = Calendar.from_ical(response.text)

            # Clear old events for this listing
            self.db.query(CalendarEvent).filter(
                CalendarEvent.listing_id == listing_id
            ).delete()

            count = 0
            for component in cal.walk():
                if component.name == "VEVENT":
                    dtstart = component.get("dtstart")
                    dtend = component.get("dtend")
                    if dtstart and dtend:
                        event = CalendarEvent(
                            listing_id=listing_id,
                            start_date=dtstart.dt,
                            end_date=dtend.dt,
                            summary=str(component.get("summary", "")),
                            source_platform=listing.platform.name if listing.platform else None,
                        )
                        self.db.add(event)
                        count += 1

            self.db.commit()
            return {"status": "ok", "events_synced": count}

        except Exception as e:
            return {"status": "error", "message": str(e)}
