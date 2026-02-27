from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    reviewer_name = Column(String, nullable=True)
    rating = Column(Float, nullable=False)
    text = Column(Text, nullable=True)
    text_translated = Column(Text, nullable=True)
    original_language = Column(String, nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    host = relationship("Host", back_populates="reviews")
    platform = relationship("Platform")
