from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.listing import ListingResponse, ListingSearchParams
from app.services.listing_service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/search", response_model=list[ListingResponse])
def search_listings(
    city: str | None = Query(None),
    country: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    price_type: str = Query("monthly"),
    property_type: str | None = Query(None),
    min_bedrooms: int | None = Query(None),
    platforms: str | None = Query(None, description="Comma-separated platform names"),
    sort_by: str = Query("price"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    params = ListingSearchParams(
        city=city,
        country=country,
        min_price=min_price,
        max_price=max_price,
        price_type=price_type,
        property_type=property_type,
        min_bedrooms=min_bedrooms,
        platforms=platforms.split(",") if platforms else None,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    service = ListingService(db)
    return service.search(params)


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    service = ListingService(db)
    return service.get_by_id(listing_id)


@router.get("/{listing_id}/compare")
def compare_listing_prices(listing_id: int, db: Session = Depends(get_db)):
    """Find the same property on other platforms and compare prices."""
    service = ListingService(db)
    return service.compare_prices(listing_id)
