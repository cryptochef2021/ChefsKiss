from app.scrapers.base import BaseScraper, ScrapedListing


class AgodaScraper(BaseScraper):
    """Scraper for Agoda — popular in Southeast Asia."""

    platform_name = "agoda"

    async def search(self, city: str, country: str, **kwargs) -> list[ScrapedListing]:
        # TODO: Implement Agoda scraping
        # Agoda uses heavy JavaScript — Playwright needed
        raise NotImplementedError("Agoda scraper not yet implemented")

    async def get_listing(self, external_id: str) -> ScrapedListing | None:
        raise NotImplementedError

    async def get_reviews(self, external_id: str) -> list[dict]:
        raise NotImplementedError
