import json
import logging
import re
from urllib.parse import quote_plus

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout

from app.scrapers.base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

AIRBNB_SEARCH_URL = "https://www.airbnb.com/s/{location}/homes"
AIRBNB_LISTING_URL = "https://www.airbnb.com/rooms/{listing_id}"


class AirbnbScraper(BaseScraper):
    """Scraper for Airbnb listings using Playwright for JS rendering.

    Airbnb embeds listing data in a deferred-state JSON blob or __NEXT_DATA__
    script tag. We render the page with Playwright, extract the JSON, and parse
    it into ScrapedListing objects. Falls back to DOM extraction if the JSON
    approach fails.
    """

    platform_name = "airbnb"

    async def _launch_page(self) -> tuple:
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = await ctx.new_page()
        return pw, browser, page

    async def search(self, city: str, country: str, **kwargs) -> list[ScrapedListing]:
        location = quote_plus(f"{city}, {country}")
        url = AIRBNB_SEARCH_URL.format(location=location)

        checkin = kwargs.get("checkin", "")
        checkout = kwargs.get("checkout", "")
        if checkin and checkout:
            url += f"?checkin={checkin}&checkout={checkout}"

        pw, browser, page = await self._launch_page()
        listings: list[ScrapedListing] = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            listings = await self._extract_search_results(page, city, country)
        except PlaywrightTimeout:
            logger.warning("Timeout loading Airbnb search for %s, %s", city, country)
        except Exception:
            logger.exception("Error scraping Airbnb search for %s, %s", city, country)
        finally:
            await browser.close()
            await pw.stop()

        return listings

    async def _extract_search_results(
        self, page: Page, city: str, country: str
    ) -> list[ScrapedListing]:
        results: list[ScrapedListing] = []

        # Try extracting from deferred-state JSON blob first
        deferred = await page.query_selector("script#data-deferred-state")
        if deferred:
            raw = await deferred.inner_text()
            try:
                data = json.loads(raw)
                results = self._parse_deferred_state(data, city, country)
                if results:
                    return results
            except json.JSONDecodeError:
                logger.debug("Could not parse deferred state JSON")

        # Fallback: extract from rendered DOM listing cards
        cards = await page.query_selector_all(
            '[itemprop="itemListElement"], [data-testid="card-container"]'
        )
        for card in cards:
            try:
                listing = await self._parse_card_element(card, city, country)
                if listing:
                    results.append(listing)
            except Exception:
                logger.debug("Failed to parse a listing card", exc_info=True)

        return results

    def _parse_deferred_state(
        self, data: dict, city: str, country: str
    ) -> list[ScrapedListing]:
        results: list[ScrapedListing] = []
        listings_raw = self._find_listings_in_json(data)

        for item in listings_raw:
            try:
                listing_obj = item.get("listing", item)
                listing_id = str(listing_obj.get("id", ""))
                if not listing_id:
                    continue

                title = listing_obj.get("name", listing_obj.get("title", ""))
                price_info = item.get("pricingQuote", item.get("pricing", {}))
                price_per_night = None
                if isinstance(price_info, dict):
                    rate = price_info.get("rate", price_info.get("price", {}))
                    if isinstance(rate, dict):
                        price_per_night = rate.get("amount", rate.get("amountFormatted"))
                    elif isinstance(rate, (int, float)):
                        price_per_night = float(rate)

                if isinstance(price_per_night, str):
                    price_per_night = (
                        float(re.sub(r"[^\d.]", "", price_per_night) or 0) or None
                    )

                lat = listing_obj.get("lat", listing_obj.get("latitude"))
                lng = listing_obj.get("lng", listing_obj.get("longitude"))

                images = []
                for pic in listing_obj.get(
                    "contextualPictures", listing_obj.get("photos", [])
                )[:5]:
                    if isinstance(pic, dict):
                        images.append(pic.get("picture", pic.get("url", "")))
                    elif isinstance(pic, str):
                        images.append(pic)

                rating = listing_obj.get("avgRating", listing_obj.get("starRating"))
                review_count = listing_obj.get("reviewsCount", 0)

                results.append(
                    ScrapedListing(
                        external_id=listing_id,
                        title=title,
                        description=None,
                        city=city,
                        country=country,
                        address=listing_obj.get("publicAddress"),
                        latitude=float(lat) if lat else None,
                        longitude=float(lng) if lng else None,
                        price_per_night=price_per_night,
                        price_per_month=price_per_night * 30 if price_per_night else None,
                        currency=listing_obj.get("listingCurrency", "USD"),
                        property_type=listing_obj.get(
                            "roomTypeCategory", listing_obj.get("propertyType")
                        ),
                        bedrooms=listing_obj.get("bedrooms"),
                        bathrooms=listing_obj.get("bathrooms"),
                        max_guests=listing_obj.get("personCapacity"),
                        listing_url=f"https://www.airbnb.com/rooms/{listing_id}",
                        image_urls=images,
                        host_name=(
                            listing_obj.get("user", {}).get("firstName")
                            if isinstance(listing_obj.get("user"), dict)
                            else None
                        ),
                        rating=float(rating) if rating else None,
                        review_count=int(review_count) if review_count else 0,
                        original_language="en",
                    )
                )
            except Exception:
                logger.debug("Failed to parse listing from deferred state", exc_info=True)

        return results

    def _find_listings_in_json(self, obj, depth: int = 0) -> list[dict]:
        """Recursively search JSON tree for listing-like objects."""
        if depth > 15:
            return []
        results = []
        if isinstance(obj, dict):
            if "listing" in obj and isinstance(obj["listing"], dict):
                results.append(obj)
            elif (
                "id" in obj
                and ("name" in obj or "title" in obj)
                and ("lat" in obj or "latitude" in obj)
            ):
                results.append(obj)
            else:
                for v in obj.values():
                    results.extend(self._find_listings_in_json(v, depth + 1))
        elif isinstance(obj, list):
            for item in obj:
                results.extend(self._find_listings_in_json(item, depth + 1))
        return results

    async def _parse_card_element(
        self, card, city: str, country: str
    ) -> ScrapedListing | None:
        """Parse a single listing card from the DOM as a fallback."""
        link_el = await card.query_selector('a[href*="/rooms/"]')
        if not link_el:
            return None

        href = await link_el.get_attribute("href") or ""
        id_match = re.search(r"/rooms/(\d+)", href)
        if not id_match:
            return None
        listing_id = id_match.group(1)

        title_el = await card.query_selector(
            '[data-testid="listing-card-title"], [id*="title"]'
        )
        title = await title_el.inner_text() if title_el else "Untitled"

        price_el = await card.query_selector(
            '[data-testid="price-availability-row"] span, ._tyxjp1'
        )
        price_text = await price_el.inner_text() if price_el else ""
        price_per_night = None
        if price_text:
            nums = re.findall(r"[\d,]+\.?\d*", price_text.replace(",", ""))
            if nums:
                price_per_night = float(nums[0])

        rating_el = await card.query_selector(
            '[aria-label*="rating"], .t1a9j9y7'
        )
        rating = None
        if rating_el:
            rating_text = await rating_el.inner_text()
            rating_nums = re.findall(r"\d+\.?\d*", rating_text)
            if rating_nums:
                rating = float(rating_nums[0])

        img_el = await card.query_selector("img")
        image_url = await img_el.get_attribute("src") if img_el else None

        return ScrapedListing(
            external_id=listing_id,
            title=title.strip(),
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
            listing_url=f"https://www.airbnb.com/rooms/{listing_id}",
            image_urls=[image_url] if image_url else [],
            host_name=None,
            rating=rating,
            review_count=0,
            original_language="en",
            ical_url=f"https://www.airbnb.com/calendar/ical/{listing_id}.ics",
        )

    async def get_listing(self, external_id: str) -> ScrapedListing | None:
        url = AIRBNB_LISTING_URL.format(listing_id=external_id)
        pw, browser, page = await self._launch_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            # Try JSON-LD structured data
            json_ld = await page.query_selector('script[type="application/ld+json"]')
            structured: dict = {}
            if json_ld:
                try:
                    structured = json.loads(await json_ld.inner_text())
                except json.JSONDecodeError:
                    pass

            title_el = await page.query_selector("h1")
            title = (
                await title_el.inner_text()
                if title_el
                else structured.get("name", "Untitled")
            )

            desc_el = await page.query_selector(
                '[data-section-id="DESCRIPTION_DEFAULT"] span, .l1nqfsv9'
            )
            description = (
                await desc_el.inner_text()
                if desc_el
                else structured.get("description")
            )

            price_el = await page.query_selector(
                '[data-testid="book-it-default"] span._tyxjp1, ._wgmchy'
            )
            price_per_night = None
            if price_el:
                pt = await price_el.inner_text()
                nums = re.findall(r"[\d,]+\.?\d*", pt.replace(",", ""))
                if nums:
                    price_per_night = float(nums[0])

            detail_items = await page.query_selector_all(
                '[data-testid="listing-details"] li, .lgx66tx'
            )
            bedrooms = bathrooms = max_guests = None
            for item in detail_items:
                text = (await item.inner_text()).lower()
                bed_match = re.search(r"(\d+)\s*bedroom", text)
                bath_match = re.search(r"(\d+)\s*bathroom", text)
                guest_match = re.search(r"(\d+)\s*guest", text)
                if bed_match:
                    bedrooms = int(bed_match.group(1))
                if bath_match:
                    bathrooms = int(bath_match.group(1))
                if guest_match:
                    max_guests = int(guest_match.group(1))

            agg_rating = structured.get("aggregateRating", {})
            rating = agg_rating.get("ratingValue") if isinstance(agg_rating, dict) else None
            review_count = agg_rating.get("reviewCount", 0) if isinstance(agg_rating, dict) else 0

            images = []
            img_els = await page.query_selector_all(
                '[data-testid="photo-viewer"] img, picture img'
            )
            for img in img_els[:10]:
                src = await img.get_attribute("src")
                if src:
                    images.append(src)

            geo = structured.get("geo", {}) if isinstance(structured, dict) else {}
            lat = geo.get("latitude")
            lng = geo.get("longitude")
            address = structured.get("address", {})
            addr_str = address.get("streetAddress") if isinstance(address, dict) else None

            host_el = await page.query_selector(
                '[data-section-id="HOST_OVERVIEW"] h2, .t1pxe1a4'
            )
            host_name = None
            if host_el:
                ht = await host_el.inner_text()
                host_match = re.search(r"Hosted by (.+)", ht)
                if host_match:
                    host_name = host_match.group(1).strip()

            return ScrapedListing(
                external_id=external_id,
                title=title.strip(),
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
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                max_guests=max_guests,
                listing_url=url,
                image_urls=images,
                host_name=host_name,
                rating=float(rating) if rating else None,
                review_count=int(review_count) if review_count else 0,
                original_language="en",
                ical_url=f"https://www.airbnb.com/calendar/ical/{external_id}.ics",
            )
        except Exception:
            logger.exception("Error scraping Airbnb listing %s", external_id)
            return None
        finally:
            await browser.close()
            await pw.stop()

    async def get_reviews(self, external_id: str) -> list[dict]:
        url = AIRBNB_LISTING_URL.format(listing_id=external_id)
        pw, browser, page = await self._launch_page()
        reviews: list[dict] = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)

            show_all = await page.query_selector(
                'button[aria-label*="reviews"], '
                '[data-testid="pdp-show-all-reviews-button"]'
            )
            if show_all:
                await show_all.click()
                await page.wait_for_timeout(2000)

            review_els = await page.query_selector_all(
                '[data-review-id], [role="listitem"]'
            )
            for el in review_els[:20]:
                text_el = await el.query_selector(
                    'span[data-testid="review-comment"], span.ll4r2nl'
                )
                reviewer_el = await el.query_selector("h2, h3, .t1pxe1a4")
                date_el = await el.query_selector("li:last-child, .s78n3tv")

                text = await text_el.inner_text() if text_el else None
                reviewer = await reviewer_el.inner_text() if reviewer_el else None
                date_str = await date_el.inner_text() if date_el else None

                if text:
                    reviews.append(
                        {
                            "reviewer_name": reviewer.strip() if reviewer else None,
                            "text": text.strip(),
                            "rating": None,
                            "date": date_str.strip() if date_str else None,
                        }
                    )
        except Exception:
            logger.exception("Error scraping Airbnb reviews for %s", external_id)
        finally:
            await browser.close()
            await pw.stop()

        return reviews
