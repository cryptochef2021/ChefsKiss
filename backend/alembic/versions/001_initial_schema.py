"""Initial schema - platforms, hosts, listings, reviews, calendar_events

Revision ID: 001
Revises:
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platforms",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("base_url", sa.String(), nullable=False),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("supports_ical", sa.Boolean(), server_default="false"),
        sa.Column("scraper_enabled", sa.Boolean(), server_default="true"),
        sa.Column("requires_local_phone", sa.Boolean(), server_default="false"),
    )

    op.create_table(
        "hosts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("aggregate_rating", sa.Float(), nullable=True),
        sa.Column("total_reviews", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "listings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("platform_id", sa.Integer(), sa.ForeignKey("platforms.id"), nullable=False),
        sa.Column("host_id", sa.Integer(), sa.ForeignKey("hosts.id"), nullable=True),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("title_translated", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("description_translated", sa.Text(), nullable=True),
        sa.Column("original_language", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("price_per_night", sa.Float(), nullable=True),
        sa.Column("price_per_month", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(), server_default="USD"),
        sa.Column("property_type", sa.String(), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Integer(), nullable=True),
        sa.Column("max_guests", sa.Integer(), nullable=True),
        sa.Column("listing_url", sa.String(), nullable=False),
        sa.Column("image_urls", sa.Text(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), server_default="0"),
        sa.Column("ical_url", sa.String(), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_listings_id", "listings", ["id"])
    op.create_index("ix_listings_city_country", "listings", ["city", "country"])
    op.create_index("ix_listings_platform_external", "listings", ["platform_id", "external_id"], unique=True)

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("host_id", sa.Integer(), sa.ForeignKey("hosts.id"), nullable=False),
        sa.Column("platform_id", sa.Integer(), sa.ForeignKey("platforms.id"), nullable=False),
        sa.Column("reviewer_name", sa.String(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("text_translated", sa.Text(), nullable=True),
        sa.Column("original_language", sa.String(), nullable=True),
        sa.Column("review_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reviews_id", "reviews", ["id"])

    op.create_table(
        "calendar_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("listing_id", sa.Integer(), sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("summary", sa.String(), nullable=True),
        sa.Column("source_platform", sa.String(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_calendar_events_id", "calendar_events", ["id"])
    op.create_index("ix_calendar_events_listing_dates", "calendar_events", ["listing_id", "start_date", "end_date"])


def downgrade() -> None:
    op.drop_table("calendar_events")
    op.drop_table("reviews")
    op.drop_table("listings")
    op.drop_table("hosts")
    op.drop_table("platforms")
