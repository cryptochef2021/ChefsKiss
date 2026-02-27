import json
import logging
import re
from urllib.parse import quote_plus

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout

from app.scrapers.base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

AGODA_SEARCH_URL = (
    "https://www.agoda.com/search?"
    "city=-1&"
    "textSrc=1&"
    "searchType=1&"
    "q={query}"
)


class AgodaScraper(BaseScraper):
    """Scraper for Agoda — popular in Southeast Asia.

    Agoda is heavily JS-rendered and uses DataDome anti-bot protection.
    We use Playwright with realistic browser fingerprints and extract
    listing data from the rendered DOM and embedded JSON state.
    """

    platform_name = "agoda"

    async def _launch_page(self) -> tuple:
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
            locale="en-US",
        )
        page = await ctx.new_page()
        return pw, browser, page

    async def search(self, city: str, country: str, **kwargs) -> list[ScrapedListing]:
        query = quote_plus(f"{city} {country}")
        url = AGODA_SEARCH_URL.format(query=query)

        checkin = kwargs.get("checkin", "")
        checkout = kwargs.get("checkout", "")
        if checkin and checkout:
            url += f"&checkIn={checkin}&checkOut={checkout}"

        pw, browser, page = await self._launch_page()
        listings: list[ScrapedListing] = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(4000)
            listings = await self._extract_search_results(page, city, country)
        except PlaywrightTimeout:
            logger.warning("Timeout loading Agoda search for %s, %s", city, country)
        except Exception:
            logger.exception("Error scraping Agoda search for %s, %s", city, country)
        finally:
            await browser.close()
            await pw.stop()

        return listings

    async def _extract_search_results(
        self, page: Page, city: str, country: str
    ) -> list[ScrapedListing]:
        results: list[ScrapedListing] = []

        # Agoda may store data in window.__NEXT_DATA__
        next_data = await page.evaluate(
            "() => window.__NEXT_DATA__ ? JSON.stringify(window.__NEXT_DATA__) : null"
        )
        if next_data:
            try:
                data = json.loads(next_data)
                results = self._parse_next_data(data, city, country)
                if results:
                    return results
            except (json.JSONDecodeError, KeyError):
                logger.debug("Could not parse __NEXT_DATA__ from Agoda")

        # Fallback: DOM extraction from property cards
        cards = await page.query_selector_all(
            '[data-selenium="hotel-item"], .PropertyCard, '
            '[data-element-name="property-card"]'
        )
        for card in cards:
            try:
                listing = await self._parse_property_card(card, city, country)
                if listing:
                    results.append(listing)
            except Exception:
                logger.debug("Failed to parse Agoda property card", exc_info=True)

        return results

    def _parse_next_data(
        self, data: dict, city: str, country: str
    ) -> list[ScrapedListing]:
        results: list[ScrapedListing] = []
        properties = self._find_properties_in_json(data)

        for prop in properties:
            try:
                hotel_id = str(
                    prop.get("hotelId", prop.get("propertyId", prop.get("id", "")))
                )
                if not hotel_id:
                    continue

                name = prop.get(
                    "hotelName", prop.get("propertyName", prop.get("name", ""))
                )

                price_info = prop.get("pricing", prop.get("deals", {}))
                price_per_night = None
                if isinstance(price_info, dict):
                    price_per_night = price_info.get(
                        "displayPrice",
                        price_info.get("price", price_info.get("crossedOutPrice")),
                    )
                elif isinstance(price_info, list) and price_info:
                    price_per_night = (
                        price_info[0].get("price", {}).get("perNight", {}).get("display")
                    )

                if isinstance(price_per_night, str):
                    price_per_night = (
                        float(re.sub(r"[^\d.]", "", price_per_night) or 0) or None
                    )

                lat = prop.get("latitude", prop.get("lat"))
                lng = prop.get("longitude", prop.get("lng"))
                address = prop.get("address", prop.get("area", {}).get("name", ""))
                if isinstance(address, dict):
                    address = address.get("full", address.get("street", ""))

                images = []
                for img in prop.get("images", prop.get("gallery", []))[:5]:
                    if isinstance(img, dict):
                        images.append(img.get("url", img.get("uri", "")))
                    elif isinstance(img, str):
                        images.append(img)

                rating = prop.get("reviewScore", prop.get("agodaReviewScore"))
                review_count = prop.get("numberOfReviews", prop.get("reviewCount", 0))

                slug = prop.get("landingPageUrl", prop.get("slug", ""))
                listing_url = (
                    f"https://www.agoda.com{slug}"
                    if slug.startswith("/")
                    else slug
                )
                if not listing_url:
                    listing_url = f"https://www.agoda.com/hotel/{hotel_id}"

                # Agoda uses 1-10 scale; normalize to 1-5
                normalized_rating = None
                if rating:
                    r = float(rating)
                    normalized_rating = r / 2 if r > 5 else r

                results.append(
                    ScrapedListing(
                        external_id=hotel_id,
                        title=name,
                        description=None,
                        city=city,
                        country=country,
                        address=address if isinstance(address, str) else None,
                        latitude=float(lat) if lat else None,
                        longitude=float(lng) if lng else None,
                        price_per_night=(
                            float(price_per_night) if price_per_night else None
                        ),
                        price_per_month=(
                            float(price_per_night) * 30 if price_per_night else None
                        ),
                        currency=prop.get("currency", "USD"),
                        property_type=prop.get(
                            "accommodationType", prop.get("propertyType")
                        ),
                        bedrooms=prop.get("bedrooms"),
                        bathrooms=prop.get("bathrooms"),
                        max_guests=prop.get("maxGuests", prop.get("maxOccupancy")),
                        listing_url=listing_url,
                        image_urls=images,
                        host_name=None,
                        rating=normalized_rating,
                        review_count=int(review_count) if review_count else 0,
                        original_language="en",
                    )
                )
            except Exception:
                logger.debug("Failed to parse Agoda property from JSON", exc_info=True)

        return results

    def _find_properties_in_json(self, obj, depth: int = 0) -> list[dict]:
        if depth > 15:
            return []
        results = []
        if isinstance(obj, dict):
            if ("hotelId" in obj or "propertyId" in obj) and (
                "hotelName" in obj or "propertyName" in obj or "name" in obj
            ):
                results.append(obj)
            else:
                for v in obj.values():
                    results.extend(self._find_properties_in_json(v, depth + 1))
        elif isinstance(obj, list):
            for item in obj:
                results.extend(self._find_properties_in_json(item, depth + 1))
        return results

    async def _parse_property_card(
        self, card, city: str, country: str
    ) -> ScrapedListing | None:
        link_el = await card.query_selector("a[href]")
        if not link_el:
            return None

        href = await link_el.get_attribute("href") or ""
        id_match = re.search(r"hotelId[=:](\d+)", href)
        hotel_id = None
        if id_match:
            hotel_id = id_match.group(1)
        else:
            hotel_id = await card.get_attribute("data-hotelid")
            if not hotel_id:
                return None

        name_el = await card.query_selector(
            '[data-selenium="hotel-name"], .PropertyCard__HotelName, h3'
        )
        name = await name_el.inner_text() if name_el else "Untitled"

        price_el = await card.query_selector(
            '[data-selenium="display-price"], .PropertyCardPrice__Value, '
            '[data-element-name="final-price"]'
        )
        price_text = await price_el.inner_text() if price_el else ""
        price_per_night = None
        if price_text:
            nums = re.findall(r"[\d,]+\.?\d*", price_text.replace(",", ""))
            if nums:
                price_per_night = float(nums[0])

        rating_el = await card.query_selector(
            '[data-selenium="review-score"], .ReviewScore__Number'
        )
        rating = None
        if rating_el:
            rating_text = await rating_el.inner_text()
            rating_nums = re.findall(r"\d+\.?\d*", rating_text)
            if rating_nums:
                r = float(rating_nums[0])
                rating = r / 2 if r > 5 else r

        img_el = await card.query_selector("img")
        image_url = await img_el.get_attribute("src") if img_el else None

        listing_url = (
            f"https://www.agoda.com{href}" if href.startswith("/") else href
        )

        return ScrapedListing(
            external_id=hotel_id,
            title=name.strip(),
            description=None,
            city=city,
            country=country,
            address=None,
            latitude=None,
            longitude=None,
            price_per_night=price_per_night,
            price_per_month=price_per_night * 30 if price_per_night else None,
            currency="USD",
            property_type=None,
            bedrooms=None,
            bathrooms=None,
            max_guests=None,
            listing_url=listing_url,
            image_urls=[image_url] if image_url else [],
            host_name=None,
            rating=rating,
            review_count=0,
            original_language="en",
        )

    async def get_listing(self, external_id: str) -> ScrapedListing | None:
        url = f"https://www.agoda.com/hotel/{external_id}"
        pw, browser, page = await self._launch_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(4000)

            # JSON-LD structured data
            json_ld_el = await page.query_selector(
                'script[type="application/ld+json"]'
            )
            structured: dict = {}
            if json_ld_el:
                try:
                    raw = await json_ld_el.inner_text()
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        for item in parsed:
                            if isinstance(item, dict) and item.get("@type") in (
                                "Hotel",
                                "LodgingBusiness",
                                "VacationRental",
                            ):
                                structured = item
                                break
                    elif isinstance(parsed, dict):
                        structured = parsed
                except json.JSONDecodeError:
                    pass

            name_el = await page.query_selector(
                '[data-selenium="hotel-header-name"], h1'
            )
            name = (
                await name_el.inner_text()
                if name_el
                else structured.get("name", "Untitled")
            )

            desc_el = await page.query_selector(
                '[data-selenium="hotel-description"], .HotelDescription'
            )
            description = (
                await desc_el.inner_text()
                if desc_el
                else structured.get("description")
            )

            price_el = await page.query_selector(
                '[data-selenium="PriceDisplay"], .PriceDisplay__Value'
            )
            price_per_night = None
            if price_el:
                pt = await price_el.inner_text()
                nums = re.findall(r"[\d,]+\.?\d*", pt.replace(",", ""))
                if nums:
                    price_per_night = float(nums[0])

            rating_el = await page.query_selector(
                '[data-selenium="review-score"], .ReviewScore__Number'
            )
            rating = None
            if rating_el:
                rt = await rating_el.inner_text()
                rnums = re.findall(r"\d+\.?\d*", rt)
                if rnums:
                    r = float(rnums[0])
                    rating = r / 2 if r > 5 else r

            review_count_el = await page.query_selector(
                '[data-selenium="review-count"], .ReviewScore__Count'
            )
            review_count = 0
            if review_count_el:
                rct = await review_count_el.inner_text()
                rc_nums = re.findall(r"[\d,]+", rct.replace(",", ""))
                if rc_nums:
                    review_count = int(rc_nums[0])

            images = []
            img_els = await page.query_selector_all(
                '[data-selenium="hotel-gallery"] img, .HeaderCe498 img'
            )
            for img in img_els[:10]:
                src = await img.get_attribute("src")
                if src and not src.startswith("data:"):
                    images.append(src)

            geo = structured.get("geo", {})
            lat = geo.get("latitude") if isinstance(geo, dict) else None
            lng = geo.get("longitude") if isinstance(geo, dict) else None
            address_obj = structured.get("address", {})
            addr_str = (
                address_obj.get("streetAddress")
                if isinstance(address_obj, dict)
                else None
            )

            return ScrapedListing(
                external_id=external_id,
                title=name.strip(),
                description=description.strip() if description else None,
                city="",
                country="",
                address=addr_str,
                latitude=float(lat) if lat else None,
                longitude=float(lng) if lng else None,
                price_per_night=price_per_night,
                price_per_month=price_per_night * 30 if price_per_night else None,
                currency="USD",
                property_type=None,
                bedrooms=None,
                bathrooms=None,
                max_guests=None,
                listing_url=url,
                image_urls=images,
                host_name=None,
                rating=rating,
                review_count=review_count,
                original_language="en",
            )
        except Exception:
            logger.exception("Error scraping Agoda listing %s", external_id)
            return None
        finally:
            await browser.close()
            await pw.stop()

    async def get_reviews(self, external_id: str) -> list[dict]:
        url = f"https://www.agoda.com/hotel/{external_id}"
        pw, browser, page = await self._launch_page()
        reviews: list[dict] = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(4000)

            review_section = await page.query_selector(
                '[data-selenium="ReviewSection"], #reviewSection'
            )
            if review_section:
                await review_section.scroll_into_view_if_needed()
                await page.wait_for_timeout(2000)

            review_els = await page.query_selector_all(
                '[data-selenium="ReviewItem"], .Review-comment'
            )
            for el in review_els[:20]:
                text_el = await el.query_selector(
                    '[data-selenium="ReviewCommentValue"], .Review-comment-bodyText'
                )
                reviewer_el = await el.query_selector(
                    '[data-selenium="reviewer-name"], .Review-comment-reviewer'
                )
                score_el = await el.query_selector(
                    '[data-selenium="reviewer-score"], .Review-comment-leftScore'
                )
                date_el = await el.query_selector(
                    '[data-selenium="review-date"], .Review-statusBar-date'
                )

                text = await text_el.inner_text() if text_el else None
                reviewer = await reviewer_el.inner_text() if reviewer_el else None
                score_text = await score_el.inner_text() if score_el else None
                date_str = await date_el.inner_text() if date_el else None

                score = None
                if score_text:
                    snums = re.findall(r"\d+\.?\d*", score_text)
                    if snums:
                        s = float(snums[0])
                        score = s / 2 if s > 5 else s

                if text:
                    reviews.append(
                        {
                            "reviewer_name": reviewer.strip() if reviewer else None,
                            "text": text.strip(),
                            "rating": score,
                            "date": date_str.strip() if date_str else None,
                        }
                    )
        except Exception:
            logger.exception("Error scraping Agoda reviews for %s", external_id)
        finally:
            await browser.close()
            await pw.stop()

        return reviews
