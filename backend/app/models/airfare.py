from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    origin: Mapped[str] = mapped_column(
        String(3),
        index=True,
    )

    destination: Mapped[str] = mapped_column(
        String(3),
        index=True,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )


class Carrier(Base):
    __tablename__ = "carriers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(20),
    )

    base_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


class FareQuote(Base):
    __tablename__ = "fare_quotes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id"),
        index=True,
    )

    carrier_id: Mapped[int] = mapped_column(
        ForeignKey("carriers.id"),
        index=True,
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("data_sources.id"),
        index=True,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        index=True,
    )

    departure_date: Mapped[date] = mapped_column(
        Date,
        index=True,
    )

    advance_purchase_days: Mapped[int] = mapped_column(
        Integer,
        index=True,
    )

    fare_class: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    base_fare: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    taxes: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    user_development_fee: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    convenience_fee: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    total_fare: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
    )

    availability_status: Mapped[str] = mapped_column(
        String(20),
        default="available",
    )

    is_outlier: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_clean: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    raw_quote_hash: Mapped[str | None] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
        index=True,
    )


class PriceIndexValue(Base):
    __tablename__ = "price_index_values"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    period_start: Mapped[date] = mapped_column(
        Date,
        index=True,
    )

    frequency: Mapped[str] = mapped_column(
        String(20),
        index=True,
    )

    route_id: Mapped[int | None] = mapped_column(
        ForeignKey("routes.id"),
        nullable=True,
        index=True,
    )

    index_value: Mapped[float] = mapped_column(
        Float,
    )

    base_value: Mapped[float] = mapped_column(
        Float,
        default=100.0,
    )

    sample_size: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )


class ScraperRun(Base):
    __tablename__ = "scraper_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("data_sources.id"),
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="running",
    )

    records_collected: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    route_id: Mapped[int | None] = mapped_column(
        ForeignKey("routes.id"),
        nullable=True,
        index=True,
    )

    reference_month: Mapped[date] = mapped_column(
        Date,
        index=True,
    )

    computed_average_fare: Mapped[float] = mapped_column(
        Float,
    )

    dgca_average_fare: Mapped[float] = mapped_column(
        Float,
    )

    absolute_error: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    percentage_error: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
class FareReference(Base):
    __tablename__ = "fare_references"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id"),
        index=True,
    )

    carrier_id: Mapped[int] = mapped_column(
        ForeignKey("carriers.id"),
        index=True,
    )

    reference_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    cabin_class: Mapped[str] = mapped_column(
        String(50),
        default="Economy",
    )

    valid_from: Mapped[date] = mapped_column(
        Date,
        index=True,
    )

    valid_until: Mapped[date] = mapped_column(
        Date,
        index=True,
    )

    minimum_base_fare: Mapped[float] = mapped_column(
        Float,
    )

    maximum_base_fare: Mapped[float] = mapped_column(
        Float,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
    )

    source_name: Mapped[str] = mapped_column(
        String(200),
    )

    source_url: Mapped[str] = mapped_column(
        String(500),
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )