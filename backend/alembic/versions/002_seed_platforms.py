"""Seed platform records

Revision ID: 002
Revises: 001
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

platforms_table = sa.table(
    "platforms",
    sa.column("name", sa.String),
    sa.column("display_name", sa.String),
    sa.column("base_url", sa.String),
    sa.column("country_code", sa.String),
    sa.column("supports_ical", sa.Boolean),
    sa.column("scraper_enabled", sa.Boolean),
    sa.column("requires_local_phone", sa.Boolean),
)


def upgrade() -> None:
    op.bulk_insert(
        platforms_table,
        [
            {
                "name": "airbnb",
                "display_name": "Airbnb",
                "base_url": "https://www.airbnb.com",
                "country_code": None,
                "supports_ical": True,
                "scraper_enabled": True,
                "requires_local_phone": False,
            },
            {
                "name": "agoda",
                "display_name": "Agoda",
                "base_url": "https://www.agoda.com",
                "country_code": None,
                "supports_ical": False,
                "scraper_enabled": True,
                "requires_local_phone": False,
            },
            {
                "name": "batdongsan",
                "display_name": "Batdongsan.com.vn",
                "base_url": "https://batdongsan.com.vn",
                "country_code": "VN",
                "supports_ical": False,
                "scraper_enabled": True,
                "requires_local_phone": True,
            },
            {
                "name": "booking",
                "display_name": "Booking.com",
                "base_url": "https://www.booking.com",
                "country_code": None,
                "supports_ical": True,
                "scraper_enabled": False,
                "requires_local_phone": False,
            },
            {
                "name": "renthub",
                "display_name": "RentHub.in.th",
                "base_url": "https://www.renthub.in.th",
                "country_code": "TH",
                "supports_ical": False,
                "scraper_enabled": False,
                "requires_local_phone": True,
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM platforms WHERE name IN ('airbnb', 'agoda', 'batdongsan', 'booking', 'renthub')"
    )
