from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    summary = Column(String, nullable=True)
    source_platform = Column(String, nullable=True)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())

    listing = relationship("Listing", back_populates="calendar_events")
