from app.scrapers.base import BaseScraper, ScrapedListing


class BatdongsanScraper(BaseScraper):
    """Scraper for Batdongsan.com.vn — Vietnam's largest property portal."""

    platform_name = "batdongsan"

    async def search(self, city: str, country: str, **kwargs) -> list[ScrapedListing]:
        # TODO: Implement Batdongsan scraping
        # Site is in Vietnamese, listings need translation
        # Uses standard HTML — BeautifulSoup is sufficient
        raise NotImplementedError("Batdongsan scraper not yet implemented")

    async def get_listing(self, external_id: str) -> ScrapedListing | None:
        raise NotImplementedError

    async def get_reviews(self, external_id: str) -> list[dict]:
        raise NotImplementedError
