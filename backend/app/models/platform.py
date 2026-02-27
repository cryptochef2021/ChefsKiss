from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g. "airbnb", "agoda"
    display_name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    country_code = Column(String, nullable=True)  # e.g. "VN", "TH", or None for global
    supports_ical = Column(Boolean, default=False)
    scraper_enabled = Column(Boolean, default=True)
    requires_local_phone = Column(Boolean, default=False)
