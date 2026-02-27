import logging
import re

import httpx
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

BASE_URL = "https://batdongsan.com.vn"

# City slug mapping for Batdongsan URL patterns
CITY_SLUGS = {
    "ho chi minh": "ho-chi-minh",
    "hcmc": "ho-chi-minh",
    "saigon": "ho-chi-minh",
    "hanoi": "ha-noi",
    "ha noi": "ha-noi",
    "da nang": "da-nang",
    "danang": "da-nang",
    "nha trang": "nha-trang",
    "hoi an": "hoi-an",
    "da lat": "da-lat",
    "dalat": "da-lat",
    "vung tau": "vung-tau",
    "phu quoc": "phu-quoc",
    "can tho": "can-tho",
    "hai phong": "hai-phong",
    "hue": "hue",
    "quy nhon": "quy-nhon",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi,en;q=0.5",
}


class BatdongsanScraper(BaseScraper):
    """Scraper for Batdongsan.com.vn — Vietnam's largest property portal.

    Site is server-rendered HTML in Vietnamese, so BeautifulSoup is sufficient.
    Listings are in Vietnamese and need translation via TranslationService.
    """

    platform_name = "batdongsan"

    async def search(self, city: str, country: str, **kwargs) -> list[ScrapedListing]:
        city_slug = CITY_SLUGS.get(city.lower().strip())
        if not city_slug:
            logger.warning("No city slug mapping for %s, trying direct", city)
            city_slug = city.lower().replace(" ", "-")

        # URL pattern: /cho-thue-can-ho-<city> (apartment for rent)
        property_type = kwargs.get("property_type", "can-ho")
        page_num = kwargs.get("page", 1)

        url = f"{BASE_URL}/cho-thue-{property_type}-{city_slug}"
        if page_num > 1:
            url += f"/p{page_num}"

        listings: list[ScrapedListing] = []

        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                listings = self._parse_search_page(soup, city, country)
        except httpx.HTTPStatusError as e:
            logger.warning(
                "HTTP %d fetching Batdongsan search: %s", e.response.status_code, url
            )
        except Exception:
            logger.exception("Error scraping Batdongsan search for %s", city)

        return listings

    def _parse_search_page(
        self, soup: BeautifulSoup, city: str, country: str
    ) -> list[ScrapedListing]:
        results: list[ScrapedListing] = []

        cards = soup.select(
            ".js__card, .re__card-full, .product-item, "
            '[class*="CardResult"], [class*="listing-item"]'
        )

        for card in cards:
            try:
                listing = self._parse_listing_card(card, city, country)
                if listing:
                    results.append(listing)
            except Exception:
                logger.debug("Failed to parse Batdongsan listing card", exc_info=True)

        return results

    def _parse_listing_card(
        self, card, city: str, country: str
    ) -> ScrapedListing | None:
        title_el = card.select_one(
            ".re__card-title, .js__card-title, .product-title a, "
            '[class*="title"] a, h3 a, .pr-title a'
        )
        if not title_el:
            return None

        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        if href and not href.startswith("http"):
            href = f"{BASE_URL}{href}"

        external_id = ""
        id_match = re.search(r"pr(\d+)", href)
        if id_match:
            external_id = id_match.group(1)
        else:
            id_match = re.search(r"/([^/]+)\.html", href)
            external_id = id_match.group(1) if id_match else href.split("/")[-1]

        if not external_id:
            return None

        price_el = card.select_one(
            ".re__card-config-price, .product-price, "
            '[class*="price"], .pr-price'
        )
        price_text = price_el.get_text(strip=True) if price_el else ""
        price_per_month = self._parse_vnd_price(price_text)

        location_el = card.select_one(
            ".re__card-location, .product-location, "
            '[class*="location"], .pr-location'
        )
        address = location_el.get_text(strip=True) if location_el else None

        img_el = card.select_one("img")
        image_url = None
        if img_el:
            image_url = (
                img_el.get("src")
                or img_el.get("data-src")
                or img_el.get("data-lazy-src")
            )

        bedrooms = bathrooms = None
        spec_els = card.select(
            ".re__card-config span, [class*='config'] span, "
            ".re__card-config-bedroom, .re__card-config-bathroom"
        )
        for spec in spec_els:
            spec_text = spec.get_text(strip=True).lower()
            spec_title = (spec.get("title") or "").lower()
            num_match = re.search(r"(\d+)", spec_text)
            if num_match:
                val = int(num_match.group(1))
                if "ngủ" in spec_text or "ngủ" in spec_title or "bedroom" in spec_title:
                    bedrooms = val
                elif (
                    "tắm" in spec_text
                    or "tắm" in spec_title
                    or "bathroom" in spec_title
                    or "toilet" in spec_text
                ):
                    bathrooms = val

        return ScrapedListing(
            external_id=external_id,
            title=title,
            description=None,
            city=city,
            country=country or "Vietnam",
            address=address,
            latitude=None,
            longitude=None,
            price_per_night=price_per_month / 30 if price_per_month else None,
            price_per_month=price_per_month,
            currency="VND",
            property_type="apartment",
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            max_guests=None,
            listing_url=href,
            image_urls=[image_url] if image_url else [],
            host_name=None,
            rating=None,
            review_count=0,
            original_language="vi",
        )

    def _parse_vnd_price(self, text: str) -> float | None:
        """Parse Vietnamese price strings like '15 triệu/tháng' or '8.5 tr/th'."""
        if not text:
            return None

        text = text.strip().lower()

        # "triệu" or "tr" = million VND
        million_match = re.search(r"([\d.,]+)\s*(triệu|tr)", text)
        if million_match:
            val = million_match.group(1).replace(",", ".")
            try:
                return float(val) * 1_000_000
            except ValueError:
                pass

        # "tỷ" = billion VND (unlikely for rent but handle)
        billion_match = re.search(r"([\d.,]+)\s*tỷ", text)
        if billion_match:
            val = billion_match.group(1).replace(",", ".")
            try:
                return float(val) * 1_000_000_000
            except ValueError:
                pass

        # Plain number
        plain_match = re.search(r"([\d.,]+)", text)
        if plain_match:
            val = plain_match.group(1).replace(".", "").replace(",", "")
            try:
                return float(val)
            except ValueError:
                pass

        return None

    async def get_listing(self, external_id: str) -> ScrapedListing | None:
        url = f"{BASE_URL}/pr{external_id}"

        try:
            async with httpx.AsyncClient(
                headers=HEADERS, timeout=30, follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                return self._parse_detail_page(soup, external_id, url)
        except httpx.HTTPStatusError as e:
            logger.warning(
                "HTTP %d fetching Batdongsan listing %s",
                e.response.status_code,
                external_id,
            )
            return None
        except Exception:
            logger.exception("Error scraping Batdongsan listing %s", external_id)
            return None

    def _parse_detail_page(
        self, soup: BeautifulSoup, external_id: str, url: str
    ) -> ScrapedListing | None:
        title_el = soup.select_one(
            ".re__pr-title, .product-detail-title, h1, .pr-title"
        )
        title = title_el.get_text(strip=True) if title_el else "Untitled"

        desc_el = soup.select_one(
            ".re__pr-description, .product-detail-description, "
            '[class*="description"], .pr-description'
        )
        description = desc_el.get_text(strip=True) if desc_el else None

        price_el = soup.select_one(
            ".re__pr-short-info-item--price, .product-price, "
            '[class*="price"], .pr-price'
        )
        price_text = price_el.get_text(strip=True) if price_el else ""
        price_per_month = self._parse_vnd_price(price_text)

        address_el = soup.select_one(
            ".re__pr-short-info-item--address, .product-address, "
            '[class*="address"], .pr-address'
        )
        address = address_el.get_text(strip=True) if address_el else None

        bedrooms = bathrooms = max_guests = None
        detail_rows = soup.select(
            ".re__pr-specs-content-item, .product-detail-specs tr, "
            '[class*="specs"] .item, .pr-specs-item'
        )
        for row in detail_rows:
            label = row.select_one(
                ".re__pr-specs-content-item-title, td:first-child, .label"
            )
            value = row.select_one(
                ".re__pr-specs-content-item-value, td:last-child, .value"
            )
            if not label or not value:
                continue

            label_text = label.get_text(strip=True).lower()
            value_text = value.get_text(strip=True)
            num_match = re.search(r"(\d+)", value_text)
            if num_match:
                val = int(num_match.group(1))
                if "phòng ngủ" in label_text or "ngủ" in label_text:
                    bedrooms = val
                elif (
                    "phòng tắm" in label_text
                    or "toilet" in label_text
                    or "tắm" in label_text
                ):
                    bathrooms = val

        images = []
        img_els = soup.select(
            ".re__media-thumb-item img, .product-gallery img, "
            '[class*="gallery"] img, .pr-gallery img'
        )
        for img in img_els[:10]:
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if src:
                if not src.startswith("http"):
                    src = f"{BASE_URL}{src}"
                images.append(src)

        contact_el = soup.select_one(
            ".re__agent-info-name, .product-contact-name, "
            '[class*="contact-name"], .pr-contact-name'
        )
        host_name = contact_el.get_text(strip=True) if contact_el else None

        lat = lng = None
        map_el = soup.select_one(
            "[data-lat][data-lng], [data-latitude][data-longitude]"
        )
        if map_el:
            lat = map_el.get("data-lat") or map_el.get("data-latitude")
            lng = map_el.get("data-lng") or map_el.get("data-longitude")

        city = ""
        if address:
            parts = [p.strip() for p in address.split(",")]
            if len(parts) >= 2:
                city = parts[-1]

        return ScrapedListing(
            external_id=external_id,
            title=title,
            description=description,
            city=city,
            country="Vietnam",
            address=address,
            latitude=float(lat) if lat else None,
            longitude=float(lng) if lng else None,
            price_per_night=price_per_month / 30 if price_per_month else None,
            price_per_month=price_per_month,
            currency="VND",
            property_type="apartment",
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            max_guests=max_guests,
            listing_url=url,
            image_urls=images,
            host_name=host_name,
            rating=None,
            review_count=0,
            original_language="vi",
        )

    async def get_reviews(self, external_id: str) -> list[dict]:
        # Batdongsan is a listing portal, not a booking platform —
        # properties don't have guest reviews on this site.
        return []
