from app.scrapers.base import BaseScraper, ScrapedListing
from app.scrapers.adapters.airbnb import AirbnbScraper
from app.scrapers.adapters.agoda import AgodaScraper
from app.scrapers.adapters.batdongsan import BatdongsanScraper

# Registry mapping platform name -> scraper class
SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "airbnb": AirbnbScraper,
    "agoda": AgodaScraper,
    "batdongsan": BatdongsanScraper,
}


def get_scraper(platform_name: str) -> BaseScraper:
    """Get a scraper instance for the given platform name."""
    cls = SCRAPER_REGISTRY.get(platform_name)
    if cls is None:
        raise ValueError(f"No scraper registered for platform: {platform_name}")
    return cls()


__all__ = [
    "BaseScraper",
    "ScrapedListing",
    "AirbnbScraper",
    "AgodaScraper",
    "BatdongsanScraper",
    "SCRAPER_REGISTRY",
    "get_scraper",
]
