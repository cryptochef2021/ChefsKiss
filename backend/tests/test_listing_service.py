import pytest
from fastapi import HTTPException

from app.schemas.listing import ListingSearchParams
from app.services.listing_service import ListingService


class TestListingService:
    def test_search_all(self, db_session):
        service = ListingService(db_session)
        params = ListingSearchParams()
        results = service.search(params)
        assert len(results) == 3

    def test_search_by_city(self, db_session):
        service = ListingService(db_session)
        params = ListingSearchParams(city="Ho Chi Minh")
        results = service.search(params)
        assert len(results) == 3
        for r in results:
            assert "Ho Chi Minh" in r.city

    def test_search_by_max_price_monthly(self, db_session):
        service = ListingService(db_session)
        params = ListingSearchParams(max_price=600, price_type="monthly")
        results = service.search(params)
        # Should include the two USD listings (500, 450)
        assert len(results) == 2
        for r in results:
            assert r.price_per_month <= 600

    def test_search_by_platform(self, db_session):
        service = ListingService(db_session)
        params = ListingSearchParams(platforms=["airbnb"])
        results = service.search(params)
        assert len(results) == 1
        assert results[0].platform_name == "Airbnb"

    def test_search_by_property_type(self, db_session):
        service = ListingService(db_session)
        params = ListingSearchParams(property_type="apartment")
        results = service.search(params)
        assert len(results) == 3

    def test_search_by_min_bedrooms(self, db_session):
        service = ListingService(db_session)
        params = ListingSearchParams(min_bedrooms=2)
        results = service.search(params)
        assert len(results) == 1
        assert results[0].bedrooms >= 2

    def test_search_sort_by_rating(self, db_session):
        service = ListingService(db_session)
        params = ListingSearchParams(sort_by="rating")
        results = service.search(params)
        # Should be sorted by rating descending
        ratings = [r.rating for r in results if r.rating is not None]
        assert ratings == sorted(ratings, reverse=True)

    def test_search_pagination(self, db_session):
        service = ListingService(db_session)
        params = ListingSearchParams(page=1, page_size=2)
        results = service.search(params)
        assert len(results) == 2

        params2 = ListingSearchParams(page=2, page_size=2)
        results2 = service.search(params2)
        assert len(results2) == 1

    def test_get_by_id(self, db_session):
        service = ListingService(db_session)
        result = service.get_by_id(1)
        assert result.id == 1
        assert result.title == "Cozy apartment in HCMC"
        assert result.platform_name == "Airbnb"
        assert result.host_name == "Test Host"

    def test_get_by_id_not_found(self, db_session):
        service = ListingService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            service.get_by_id(999)
        assert exc_info.value.status_code == 404

    def test_compare_prices(self, db_session):
        service = ListingService(db_session)
        result = service.compare_prices(1)
        assert result["listing_id"] == 1
        # Both listings belong to host_id=1, same city
        assert len(result["comparisons"]) == 2
        platforms = {c["platform"] for c in result["comparisons"]}
        assert "Airbnb" in platforms
        assert "Agoda" in platforms

    def test_compare_prices_no_host(self, db_session):
        service = ListingService(db_session)
        # Listing 3 has no host_id
        result = service.compare_prices(3)
        assert result["comparisons"] == []
