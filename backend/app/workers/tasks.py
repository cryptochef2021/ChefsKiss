from app.workers.celery_app import celery_app


@celery_app.task
def sync_all_calendars():
    """Sync iCal calendars for all listings that have an iCal URL."""
    # TODO: Iterate all listings with ical_url and sync each
    pass


@celery_app.task
def scrape_all_platforms():
    """Run scrapers for all enabled platforms."""
    # TODO: Run each enabled scraper and store results
    pass


@celery_app.task
def translate_listing(listing_id: int):
    """Translate a listing's title and description."""
    # TODO: Fetch listing, detect language, translate if not English
    pass
