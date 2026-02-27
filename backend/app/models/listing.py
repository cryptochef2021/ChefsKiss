from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=True)
    external_id = Column(String, nullable=False)  # ID on the source platform
    title = Column(String, nullable=False)
    title_translated = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    description_translated = Column(Text, nullable=True)
    original_language = Column(String, nullable=True)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    price_per_night = Column(Float, nullable=True)
    price_per_month = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    property_type = Column(String, nullable=True)  # apartment, house, studio, etc.
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    max_guests = Column(Integer, nullable=True)
    listing_url = Column(String, nullable=False)
    image_urls = Column(Text, nullable=True)  # JSON array of URLs
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    ical_url = Column(String, nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    platform = relationship("Platform")
    host = relationship("Host", back_populates="listings")
    calendar_events = relationship("CalendarEvent", back_populates="listing")
