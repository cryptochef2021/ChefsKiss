import pytest

from app.scrapers import get_scraper, SCRAPER_REGISTRY
from app.scrapers.base import ScrapedListing
from app.scrapers.adapters.airbnb import AirbnbScraper
from app.scrapers.adapters.agoda import AgodaScraper
from app.scrapers.adapters.batdongsan import BatdongsanScraper


class TestScraperRegistry:
    def test_registry_has_all_platforms(self):
        assert "airbnb" in SCRAPER_REGISTRY
        assert "agoda" in SCRAPER_REGISTRY
        assert "batdongsan" in SCRAPER_REGISTRY

    def test_get_scraper_airbnb(self):
        scraper = get_scraper("airbnb")
        assert isinstance(scraper, AirbnbScraper)
        assert scraper.platform_name == "airbnb"

    def test_get_scraper_agoda(self):
        scraper = get_scraper("agoda")
        assert isinstance(scraper, AgodaScraper)
        assert scraper.platform_name == "agoda"

    def test_get_scraper_batdongsan(self):
        scraper = get_scraper("batdongsan")
        assert isinstance(scraper, BatdongsanScraper)
        assert scraper.platform_name == "batdongsan"

    def test_get_scraper_unknown(self):
        with pytest.raises(ValueError, match="No scraper registered"):
            get_scraper("unknown_platform")


class TestBatdongsanPriceParser:
    """Test Vietnamese price string parsing."""

    def setup_method(self):
        self.scraper = BatdongsanScraper()

    def test_parse_trieu_per_month(self):
        assert self.scraper._parse_vnd_price("15 triệu/tháng") == 15_000_000

    def test_parse_tr_per_month(self):
        assert self.scraper._parse_vnd_price("8.5 tr/th") == 8_500_000

    def test_parse_trieu_decimal(self):
        assert self.scraper._parse_vnd_price("12,5 triệu") == 12_500_000

    def test_parse_ty(self):
        assert self.scraper._parse_vnd_price("1.2 tỷ") == 1_200_000_000

    def test_parse_empty(self):
        assert self.scraper._parse_vnd_price("") is None

    def test_parse_none(self):
        assert self.scraper._parse_vnd_price("") is None

    def test_parse_plain_number(self):
        result = self.scraper._parse_vnd_price("5000000")
        assert result == 5_000_000


class TestAirbnbJsonParsing:
    """Test Airbnb deferred state JSON parsing."""

    def setup_method(self):
        self.scraper = AirbnbScraper()

    def test_find_listings_in_nested_json(self):
        data = {
            "niobeMinimalClientData": [
                [
                    "key",
                    {
                        "data": {
                            "presentation": {
                                "searchResults": [
                                    {
                                        "listing": {
                                            "id": "123",
                                            "name": "Test Listing",
                                            "lat": 10.0,
                                            "lng": 106.0,
                                        },
                                        "pricingQuote": {
                                            "rate": {"amount": 25.0}
                                        },
                                    }
                                ]
                            }
                        }
                    },
                ]
            ]
        }
        results = self.scraper._find_listings_in_json(data)
        assert len(results) == 1
        assert results[0]["listing"]["id"] == "123"

    def test_find_listings_flat_format(self):
        data = [
            {
                "id": "456",
                "name": "Flat Listing",
                "lat": 10.5,
                "lng": 107.0,
            }
        ]
        results = self.scraper._find_listings_in_json(data)
        assert len(results) == 1
        assert results[0]["id"] == "456"

    def test_find_listings_empty(self):
        results = self.scraper._find_listings_in_json({})
        assert results == []

    def test_parse_deferred_state(self):
        data = {
            "results": [
                {
                    "listing": {
                        "id": "789",
                        "name": "Test Place",
                        "lat": 13.75,
                        "lng": 100.5,
                        "bedrooms": 2,
                        "bathrooms": 1,
                        "personCapacity": 4,
                        "reviewsCount": 42,
                        "avgRating": 4.7,
                        "roomTypeCategory": "entire_home",
                        "contextualPictures": [
                            {"picture": "https://img.example.com/1.jpg"}
                        ],
                    },
                    "pricingQuote": {"rate": {"amount": 35.0}},
                }
            ]
        }
        results = self.scraper._parse_deferred_state(data, "Bangkok", "Thailand")
        assert len(results) == 1
        listing = results[0]
        assert listing.external_id == "789"
        assert listing.title == "Test Place"
        assert listing.price_per_night == 35.0
        assert listing.price_per_month == 1050.0
        assert listing.bedrooms == 2
        assert listing.rating == 4.7
        assert listing.city == "Bangkok"
        assert listing.country == "Thailand"


class TestAgodaJsonParsing:
    """Test Agoda property JSON parsing."""

    def setup_method(self):
        self.scraper = AgodaScraper()

    def test_find_properties(self):
        data = {
            "props": {
                "pageProps": {
                    "searchResult": {
                        "properties": [
                            {
                                "hotelId": 100,
                                "hotelName": "Test Hotel",
                                "latitude": 13.7,
                                "longitude": 100.5,
                            }
                        ]
                    }
                }
            }
        }
        results = self.scraper._find_properties_in_json(data)
        assert len(results) == 1
        assert results[0]["hotelId"] == 100

    def test_find_properties_empty(self):
        results = self.scraper._find_properties_in_json({})
        assert results == []

    def test_rating_normalization(self):
        """Agoda uses 1-10 scale, should normalize to 1-5."""
        data = {
            "properties": [
                {
                    "hotelId": 200,
                    "hotelName": "Rated Hotel",
                    "reviewScore": 8.6,
                    "numberOfReviews": 100,
                    "latitude": 10.0,
                    "longitude": 106.0,
                }
            ]
        }
        results = self.scraper._parse_next_data(
            data, "Ho Chi Minh City", "Vietnam"
        )
        assert len(results) == 1
        assert results[0].rating == pytest.approx(4.3, abs=0.01)


class TestScrapedListing:
    def test_create_listing(self):
        listing = ScrapedListing(
            external_id="test-1",
            title="Test Listing",
            description="A test",
            city="Bangkok",
            country="Thailand",
            address="123 Test St",
            latitude=13.75,
            longitude=100.5,
            price_per_night=30.0,
            price_per_month=900.0,
            currency="USD",
            property_type="apartment",
            bedrooms=1,
            bathrooms=1,
            max_guests=2,
            listing_url="https://example.com/test",
            image_urls=["https://img.example.com/1.jpg"],
            host_name="Test Host",
            rating=4.5,
            review_count=10,
            original_language="en",
            ical_url="https://example.com/ical/test.ics",
        )
        assert listing.external_id == "test-1"
        assert listing.ical_url == "https://example.com/ical/test.ics"
        assert listing.price_per_month == 900.0
