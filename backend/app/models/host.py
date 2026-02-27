from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    aggregate_rating = Column(Float, nullable=True)
    total_reviews = Column(Integer, default=0)

    listings = relationship("Listing", back_populates="host")
    reviews = relationship("Review", back_populates="host")
