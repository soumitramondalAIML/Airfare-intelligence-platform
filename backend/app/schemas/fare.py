from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FareQuoteCreate(BaseModel):
    route_id: int = Field(gt=0)
    carrier_id: int = Field(gt=0)
    source_id: int = Field(gt=0)

    departure_date: date

    advance_purchase_days: int = Field(
        gt=0,
    )

    fare_class: str | None = None

    base_fare: float | None = Field(
        default=None,
        ge=0,
    )

    taxes: float | None = Field(
        default=None,
        ge=0,
    )

    user_development_fee: float | None = Field(
        default=None,
        ge=0,
    )

    convenience_fee: float | None = Field(
        default=None,
        ge=0,
    )

    total_fare: float | None = Field(
        default=None,
        ge=0,
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    availability_status: str = "available"


class FareQuoteResponse(BaseModel):
    id: int

    route_id: int
    carrier_id: int
    source_id: int

    collected_at: datetime
    departure_date: date

    advance_purchase_days: int

    fare_class: str | None

    base_fare: float | None
    taxes: float | None
    user_development_fee: float | None
    convenience_fee: float | None
    total_fare: float | None

    currency: str
    availability_status: str

    is_outlier: bool
    is_clean: bool

    model_config = ConfigDict(
        from_attributes=True,
    )