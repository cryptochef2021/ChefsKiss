from app.scrapers.base import BaseScraper, ScrapedListing


class AirbnbScraper(BaseScraper):
    """Scraper for Airbnb listings."""

    platform_name = "airbnb"

    async def search(self, city: str, country: str, **kwargs) -> list[ScrapedListing]:
        # TODO: Implement Airbnb search scraping
        # Airbnb has a GraphQL API that can be reverse-engineered
        # or use their public search page with Playwright
        raise NotImplementedError("Airbnb scraper not yet implemented")

    async def get_listing(self, external_id: str) -> ScrapedListing | None:
        raise NotImplementedError

    async def get_reviews(self, external_id: str) -> list[dict]:
        raise NotImplementedError
