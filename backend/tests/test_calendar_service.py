from datetime import date
from unittest.mock import patch, MagicMock

from app.models.calendar_event import CalendarEvent
from app.services.calendar_service import CalendarService


SAMPLE_ICAL = """\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART;VALUE=DATE:20260315
DTEND;VALUE=DATE:20260320
SUMMARY:Reserved
UID:test-event-1@airbnb.com
END:VEVENT
BEGIN:VEVENT
DTSTART;VALUE=DATE:20260401
DTEND;VALUE=DATE:20260405
SUMMARY:Not available
UID:test-event-2@airbnb.com
END:VEVENT
END:VCALENDAR
"""


class TestCalendarService:
    def test_get_availability_empty(self, db_session):
        service = CalendarService(db_session)
        result = service.get_availability(1)
        assert result["listing_id"] == 1
        assert result["blocked_dates"] == []

    def test_get_availability_with_events(self, db_session):
        event = CalendarEvent(
            listing_id=1,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
            summary="Reserved",
            source_platform="airbnb",
        )
        db_session.add(event)
        db_session.commit()

        service = CalendarService(db_session)
        result = service.get_availability(1)
        assert len(result["blocked_dates"]) == 1
        assert result["blocked_dates"][0]["start"] == "2026-06-01"
        assert result["blocked_dates"][0]["end"] == "2026-06-05"
        assert result["blocked_dates"][0]["source"] == "airbnb"

    @patch("app.services.calendar_service.httpx.get")
    def test_sync_ical(self, mock_get, db_session):
        mock_response = MagicMock()
        mock_response.text = SAMPLE_ICAL
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        service = CalendarService(db_session)
        result = service.sync(1)  # Listing 1 has ical_url set

        assert result["status"] == "ok"
        assert result["events_synced"] == 2

        # Verify events were stored
        events = (
            db_session.query(CalendarEvent)
            .filter(CalendarEvent.listing_id == 1)
            .all()
        )
        assert len(events) == 2

    def test_sync_no_ical_url(self, db_session):
        service = CalendarService(db_session)
        result = service.sync(2)  # Listing 2 has no ical_url
        assert result["status"] == "error"
        assert "No iCal URL" in result["message"]

    def test_sync_listing_not_found(self, db_session):
        service = CalendarService(db_session)
        result = service.sync(999)
        assert result["status"] == "error"
