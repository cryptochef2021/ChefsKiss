import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Listing, Platform, Host, Review, CalendarEvent  # noqa: F401


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    # Seed platforms
    platforms = [
        Platform(
            id=1,
            name="airbnb",
            display_name="Airbnb",
            base_url="https://www.airbnb.com",
            supports_ical=True,
            scraper_enabled=True,
        ),
        Platform(
            id=2,
            name="agoda",
            display_name="Agoda",
            base_url="https://www.agoda.com",
            supports_ical=False,
            scraper_enabled=True,
        ),
        Platform(
            id=3,
            name="batdongsan",
            display_name="Batdongsan.com.vn",
            base_url="https://batdongsan.com.vn",
            country_code="VN",
            supports_ical=False,
            scraper_enabled=True,
            requires_local_phone=True,
        ),
    ]
    for p in platforms:
        session.add(p)

    # Seed a host
    host = Host(id=1, name="Test Host", aggregate_rating=4.5, total_reviews=10)
    session.add(host)

    # Seed listings
    listings = [
        Listing(
            id=1,
            platform_id=1,
            host_id=1,
            external_id="12345",
            title="Cozy apartment in HCMC",
            description="A nice place to stay",
            city="Ho Chi Minh City",
            country="Vietnam",
            price_per_night=25.0,
            price_per_month=500.0,
            currency="USD",
            property_type="apartment",
            bedrooms=1,
            bathrooms=1,
            max_guests=2,
            listing_url="https://www.airbnb.com/rooms/12345",
            rating=4.8,
            review_count=50,
            ical_url="https://www.airbnb.com/calendar/ical/12345.ics",
        ),
        Listing(
            id=2,
            platform_id=2,
            host_id=1,
            external_id="67890",
            title="Cozy apartment in HCMC",
            description="Same place on Agoda",
            city="Ho Chi Minh City",
            country="Vietnam",
            price_per_night=22.0,
            price_per_month=450.0,
            currency="USD",
            property_type="apartment",
            bedrooms=1,
            bathrooms=1,
            max_guests=2,
            listing_url="https://www.agoda.com/hotel/67890",
            rating=4.5,
            review_count=30,
        ),
        Listing(
            id=3,
            platform_id=3,
            external_id="99999",
            title="Căn hộ cho thuê quận 1",
            description="Căn hộ đẹp tại trung tâm thành phố",
            city="Ho Chi Minh City",
            country="Vietnam",
            price_per_month=15000000.0,
            currency="VND",
            property_type="apartment",
            bedrooms=2,
            bathrooms=1,
            listing_url="https://batdongsan.com.vn/pr99999",
            original_language="vi",
        ),
    ]
    for l in listings:
        session.add(l)

    session.commit()
    yield session
    session.close()
