import asyncio
import json
import logging

from app.core.database import SessionLocal
from app.models.listing import Listing
from app.models.platform import Platform
from app.models.host import Host
from app.scrapers import get_scraper, SCRAPER_REGISTRY
from app.services.calendar_service import CalendarService
from app.services.translation_service import TranslationService
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def sync_all_calendars(self):
    """Sync iCal calendars for all listings that have an iCal URL."""
    db = SessionLocal()
    try:
        listings = (
            db.query(Listing)
            .filter(Listing.ical_url.isnot(None), Listing.ical_url != "")
            .all()
        )
        logger.info("Syncing calendars for %d listings", len(listings))

        cal_service = CalendarService(db)
        synced = 0
        errors = 0

        for listing in listings:
            try:
                result = cal_service.sync(listing.id)
                if result.get("status") == "ok":
                    synced += 1
                    logger.debug(
                        "Synced %d events for listing %d",
                        result.get("events_synced", 0),
                        listing.id,
                    )
                else:
                    errors += 1
                    logger.warning(
                        "Calendar sync failed for listing %d: %s",
                        listing.id,
                        result.get("message"),
                    )
            except Exception:
                errors += 1
                logger.exception(
                    "Exception syncing calendar for listing %d", listing.id
                )

        logger.info(
            "Calendar sync complete: %d synced, %d errors out of %d total",
            synced,
            errors,
            len(listings),
        )
        return {"synced": synced, "errors": errors, "total": len(listings)}
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def scrape_all_platforms(self):
    """Run scrapers for all enabled platforms and store results."""
    db = SessionLocal()
    try:
        platforms = (
            db.query(Platform).filter(Platform.scraper_enabled.is_(True)).all()
        )
        logger.info("Running scrapers for %d enabled platforms", len(platforms))

        total_new = 0
        total_updated = 0
        total_errors = 0

        scrape_targets = _get_scrape_targets(platforms)

        for platform, cities in scrape_targets:
            if platform.name not in SCRAPER_REGISTRY:
                logger.warning(
                    "No scraper registered for platform: %s", platform.name
                )
                continue

            scraper = get_scraper(platform.name)
            for city, country in cities:
                try:
                    listings = _run_async(scraper.search(city, country))
                    new, updated = _upsert_listings(db, platform, listings)
                    total_new += new
                    total_updated += updated
                    logger.info(
                        "Scraped %s/%s/%s: %d new, %d updated",
                        platform.name,
                        city,
                        country,
                        new,
                        updated,
                    )
                except Exception:
                    total_errors += 1
                    logger.exception(
                        "Error scraping %s for %s, %s",
                        platform.name,
                        city,
                        country,
                    )

        logger.info(
            "Scrape complete: %d new, %d updated, %d errors",
            total_new,
            total_updated,
            total_errors,
        )
        return {
            "new": total_new,
            "updated": total_updated,
            "errors": total_errors,
        }
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def translate_listing(self, listing_id: int):
    """Translate a listing's title and description if not in English."""
    db = SessionLocal()
    try:
        listing = db.query(Listing).filter(Listing.id == listing_id).first()
        if not listing:
            logger.warning("Listing %d not found for translation", listing_id)
            return {"status": "not_found"}

        if listing.original_language == "en":
            return {"status": "already_english"}

        if listing.title_translated and listing.description_translated:
            return {"status": "already_translated"}

        translator = TranslationService()
        translated_fields = {}

        if listing.title and not listing.title_translated:
            translated = _run_async(
                translator.translate(listing.title, target_lang="EN")
            )
            if translated:
                listing.title_translated = translated
                translated_fields["title"] = True

        if listing.description and not listing.description_translated:
            translated = _run_async(
                translator.translate(listing.description, target_lang="EN")
            )
            if translated:
                listing.description_translated = translated
                translated_fields["description"] = True

        db.commit()
        logger.info(
            "Translated listing %d: %s",
            listing_id,
            ", ".join(translated_fields.keys()) or "nothing to translate",
        )
        return {"status": "ok", "translated": list(translated_fields.keys())}
    except Exception as exc:
        logger.exception("Error translating listing %d", listing_id)
        raise self.retry(exc=exc)
    finally:
        db.close()


def _get_scrape_targets(
    platforms: list[Platform],
) -> list[tuple[Platform, list[tuple[str, str]]]]:
    """Build a list of (platform, [(city, country)]) targets to scrape."""
    sea_cities = [
        ("Ho Chi Minh City", "Vietnam"),
        ("Hanoi", "Vietnam"),
        ("Da Nang", "Vietnam"),
        ("Bangkok", "Thailand"),
        ("Chiang Mai", "Thailand"),
        ("Phuket", "Thailand"),
        ("Bali", "Indonesia"),
        ("Kuala Lumpur", "Malaysia"),
    ]

    vietnam_cities = [
        ("Ho Chi Minh City", "Vietnam"),
        ("Hanoi", "Vietnam"),
        ("Da Nang", "Vietnam"),
        ("Nha Trang", "Vietnam"),
        ("Da Lat", "Vietnam"),
        ("Hoi An", "Vietnam"),
        ("Phu Quoc", "Vietnam"),
    ]

    targets = []
    for platform in platforms:
        if platform.country_code == "VN":
            targets.append((platform, vietnam_cities))
        else:
            targets.append((platform, sea_cities))

    return targets


def _upsert_listings(db, platform: Platform, scraped_listings) -> tuple[int, int]:
    """Insert new listings or update existing ones. Returns (new_count, updated_count)."""
    new_count = 0
    updated_count = 0

    for scraped in scraped_listings:
        existing = (
            db.query(Listing)
            .filter(
                Listing.platform_id == platform.id,
                Listing.external_id == scraped.external_id,
            )
            .first()
        )

        # Find or create host
        host = None
        if scraped.host_name:
            host = db.query(Host).filter(Host.name == scraped.host_name).first()
            if not host:
                host = Host(name=scraped.host_name)
                db.add(host)
                db.flush()

        image_urls_json = (
            json.dumps(scraped.image_urls) if scraped.image_urls else None
        )

        if existing:
            existing.title = scraped.title
            existing.description = scraped.description
            existing.price_per_night = scraped.price_per_night
            existing.price_per_month = scraped.price_per_month
            existing.currency = scraped.currency
            existing.property_type = scraped.property_type
            existing.bedrooms = scraped.bedrooms
            existing.bathrooms = scraped.bathrooms
            existing.max_guests = scraped.max_guests
            existing.rating = scraped.rating
            existing.review_count = scraped.review_count
            existing.listing_url = scraped.listing_url
            existing.image_urls = image_urls_json
            existing.latitude = scraped.latitude
            existing.longitude = scraped.longitude
            existing.address = scraped.address
            existing.original_language = scraped.original_language
            if scraped.ical_url:
                existing.ical_url = scraped.ical_url
            if host:
                existing.host_id = host.id
            updated_count += 1

            # Queue translation if needed
            if scraped.original_language and scraped.original_language != "en":
                if not existing.title_translated:
                    translate_listing.delay(existing.id)
        else:
            listing = Listing(
                platform_id=platform.id,
                host_id=host.id if host else None,
                external_id=scraped.external_id,
                title=scraped.title,
                description=scraped.description,
                city=scraped.city,
                country=scraped.country,
                address=scraped.address,
                latitude=scraped.latitude,
                longitude=scraped.longitude,
                price_per_night=scraped.price_per_night,
                price_per_month=scraped.price_per_month,
                currency=scraped.currency,
                property_type=scraped.property_type,
                bedrooms=scraped.bedrooms,
                bathrooms=scraped.bathrooms,
                max_guests=scraped.max_guests,
                listing_url=scraped.listing_url,
                image_urls=image_urls_json,
                rating=scraped.rating,
                review_count=scraped.review_count,
                original_language=scraped.original_language,
                ical_url=scraped.ical_url,
            )
            db.add(listing)
            db.flush()
            new_count += 1

            # Queue translation for non-English listings
            if scraped.original_language and scraped.original_language != "en":
                translate_listing.delay(listing.id)

    db.commit()
    return new_count, updated_count
