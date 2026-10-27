
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            "width_cm IS NULL OR width_cm > 0",
            name="ck_products_width_positive",
        ),
        CheckConstraint(
            "depth_cm IS NULL OR depth_cm > 0",
            name="ck_products_depth_positive",
        ),
        CheckConstraint(
            "height_cm IS NULL OR height_cm > 0",
            name="ck_products_height_positive",
        ),
        Index("ix_products_category", "category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    brand: Mapped[str | None] = mapped_column(String(150))
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    width_cm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    depth_cm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    color_name: Mapped[str | None] = mapped_column(String(100))
    color_hex: Mapped[str | None] = mapped_column(String(7))
    material: Mapped[str | None] = mapped_column(String(200))
    image_main: Mapped[str | None] = mapped_column(Text)

    style_tags: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    canonical_group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        index=True,
    )
    match_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 3)
    )


    rating_average: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    rating_count: Mapped[int | None] = mapped_column(Integer)

    one_star_share: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    five_star_share: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    reviews_read_count: Mapped[int | None] = mapped_column(Integer)

    review_summary: Mapped[str | None] = mapped_column(Text)

    review_sources: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    themes_positive: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    themes_negative: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    review_extracts: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    faithfulness_check: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    source_url: Mapped[str | None] = mapped_column(Text)
    fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    fetch_method: Mapped[str | None] = mapped_column(String(30))
    data_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    created_by: Mapped[str] = mapped_column(
        String(20),
        default="pipeline",
        nullable=False,
    )
    trace_id: Mapped[str | None] = mapped_column(String(100))
    schema_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    offers: Mapped[list["Offer"]] = relationship(
        back_populates="product",
    )


class Offer(TimestampMixin, Base):
    __tablename__ = "offers"

    __table_args__ = (
        CheckConstraint(
            "price_amount >= 0",
            name="ck_offers_price_nonnegative",
        ),
        UniqueConstraint(
            "store_name",
            "store_product_url",
            name="uq_offer_store_product_url",
        ),
        Index("ix_offers_product_id", "product_id"),
        Index("ix_offers_store_stock", "store_name", "stock_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    store_name: Mapped[str] = mapped_column(String(100), nullable=False)
    store_product_url: Mapped[str] = mapped_column(Text, nullable=False)
    price_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    stock_status: Mapped[str] = mapped_column(
        String(20),
        default="unknown",
        nullable=False,
    )

    return_window_days: Mapped[int | None] = mapped_column(Integer)
    return_policy_url: Mapped[str | None] = mapped_column(Text)

    live_check: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    image_render_allowed: Mapped[bool | None] = mapped_column(Boolean)
    price_history: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    affiliate_network: Mapped[str | None] = mapped_column(String(100))
    link_template: Mapped[str | None] = mapped_column(Text)

    source_url: Mapped[str | None] = mapped_column(Text)
    fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    fetch_method: Mapped[str | None] = mapped_column(String(30))
    data_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    created_by: Mapped[str] = mapped_column(
        String(20),
        default="pipeline",
        nullable=False,
    )
    trace_id: Mapped[str | None] = mapped_column(String(100))
    schema_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    product: Mapped["Product"] = relationship(
        back_populates="offers",
    )
