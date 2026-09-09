from dataclasses import dataclass
from datetime import date


@dataclass
class ScrapedFare:
    origin: str
    destination: str

    carrier_code: str
    source_code: str

    departure_date: date
    advance_purchase_days: int

    fare_class: str | None

    base_fare: float | None
    taxes: float | None
    user_development_fee: float | None
    convenience_fee: float | None
    total_fare: float | None

    currency: str = "INR"
    availability_status: str = "available"