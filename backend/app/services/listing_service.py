from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.listing import Listing
from app.models.platform import Platform
from app.models.host import Host
from app.schemas.listing import ListingSearchParams, ListingResponse


class ListingService:
    def __init__(self, db: Session):
        self.db = db

    def search(self, params: ListingSearchParams) -> list[ListingResponse]:
        query = self.db.query(Listing).join(Platform).outerjoin(Host)

        filters = []
        if params.city:
            filters.append(Listing.city.ilike(f"%{params.city}%"))
        if params.country:
            filters.append(Listing.country.ilike(f"%{params.country}%"))
        if params.property_type:
            filters.append(Listing.property_type == params.property_type)
        if params.min_bedrooms:
            filters.append(Listing.bedrooms >= params.min_bedrooms)
        if params.platforms:
            filters.append(Platform.name.in_(params.platforms))

        price_col = (
            Listing.price_per_month
            if params.price_type == "monthly"
            else Listing.price_per_night
        )
        if params.min_price:
            filters.append(price_col >= params.min_price)
        if params.max_price:
            filters.append(price_col <= params.max_price)

        if filters:
            query = query.filter(and_(*filters))

        sort_map = {
            "price": price_col.asc().nullslast(),
            "rating": Listing.rating.desc().nullslast(),
            "reviews": Listing.review_count.desc().nullslast(),
        }
        query = query.order_by(sort_map.get(params.sort_by, price_col.asc()))

        offset = (params.page - 1) * params.page_size
        results = query.offset(offset).limit(params.page_size).all()

        return [self._to_response(listing) for listing in results]

    def get_by_id(self, listing_id: int) -> ListingResponse:
        listing = self.db.query(Listing).filter(Listing.id == listing_id).first()
        if not listing:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Listing not found")
        return self._to_response(listing)

    def compare_prices(self, listing_id: int) -> dict:
        listing = self.db.query(Listing).filter(Listing.id == listing_id).first()
        if not listing or not listing.host_id:
            return {"listing_id": listing_id, "comparisons": []}

        same_host_listings = (
            self.db.query(Listing)
            .join(Platform)
            .filter(
                Listing.host_id == listing.host_id,
                Listing.city == listing.city,
            )
            .all()
        )

        return {
            "listing_id": listing_id,
            "comparisons": [
                {
                    "platform": l.platform.display_name if l.platform else "Unknown",
                    "price_per_night": l.price_per_night,
                    "price_per_month": l.price_per_month,
                    "currency": l.currency,
                    "url": l.listing_url,
                }
                for l in same_host_listings
            ],
        }

    def _to_response(self, listing: Listing) -> ListingResponse:
        return ListingResponse(
            id=listing.id,
            title=listing.title,
            title_translated=listing.title_translated,
            description_translated=listing.description_translated,
            city=listing.city,
            country=listing.country,
            price_per_night=listing.price_per_night,
            price_per_month=listing.price_per_month,
            currency=listing.currency,
            property_type=listing.property_type,
            bedrooms=listing.bedrooms,
            bathrooms=listing.bathrooms,
            max_guests=listing.max_guests,
            platform_name=(
                listing.platform.display_name if listing.platform else None
            ),
            host_name=listing.host.name if listing.host else None,
            latitude=listing.latitude,
            longitude=listing.longitude,
            listing_url=listing.listing_url,
            rating=listing.rating,
            review_count=listing.review_count,
            aggregate_host_rating=(
                listing.host.aggregate_rating if listing.host else None
            ),
            total_host_reviews=(
                listing.host.total_reviews if listing.host else 0
            ),
            scraped_at=listing.scraped_at,
        )
