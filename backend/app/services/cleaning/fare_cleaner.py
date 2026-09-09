from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FareQuote


VALID_AVAILABILITY_STATUSES = {
    "available",
    "sold_out",
    "cancelled",
}


def calculate_total_fare(
    quote: FareQuote,
) -> float | None:
    if quote.total_fare is not None:
        return quote.total_fare

    components = [
        quote.base_fare,
        quote.taxes,
        quote.user_development_fee,
        quote.convenience_fee,
    ]

    available_components = [
        component
        for component in components
        if component is not None
    ]

    if not available_components:
        return None

    return float(sum(available_components))


def percentile(
    values: list[float],
    percent: float,
) -> float:
    if not values:
        raise ValueError("Cannot calculate percentile of empty list")

    sorted_values = sorted(values)

    if len(sorted_values) == 1:
        return sorted_values[0]

    position = (
        (len(sorted_values) - 1)
        * percent
    )

    lower_index = int(position)
    upper_index = min(
        lower_index + 1,
        len(sorted_values) - 1,
    )

    fraction = position - lower_index

    return (
        sorted_values[lower_index]
        + (
            sorted_values[upper_index]
            - sorted_values[lower_index]
        )
        * fraction
    )


def calculate_outlier_bounds(
    values: list[float],
) -> tuple[float, float] | None:
    if len(values) < 4:
        return None

    q1 = percentile(
        values,
        0.25,
    )

    q3 = percentile(
        values,
        0.75,
    )

    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    return (
        lower_bound,
        upper_bound,
    )


def clean_fare_quotes(
    db: Session,
) -> dict[str, int]:
    quotes = db.scalars(
        select(FareQuote)
        .where(FareQuote.is_clean.is_(False))
        .order_by(FareQuote.id)
    ).all()

    processed = 0
    cleaned = 0
    outliers = 0
    rejected = 0

    groups: dict[
        tuple[int, int],
        list[FareQuote],
    ] = defaultdict(list)

    for quote in quotes:
        processed += 1

        quote.currency = quote.currency.upper()

        quote.availability_status = (
            quote.availability_status
            .strip()
            .lower()
        )

        if (
            quote.availability_status
            not in VALID_AVAILABILITY_STATUSES
        ):
            rejected += 1
            continue

        if quote.availability_status != "available":
            quote.is_outlier = False
            quote.is_clean = True

            cleaned += 1
            continue

        total_fare = calculate_total_fare(
            quote
        )

        if (
            total_fare is None
            or total_fare <= 0
        ):
            rejected += 1
            continue

        quote.total_fare = total_fare

        if quote.currency != "INR":
            rejected += 1
            continue

        groups[
            (
                quote.route_id,
                quote.advance_purchase_days,
            )
        ].append(quote)

    for group_quotes in groups.values():
        values = [
            quote.total_fare
            for quote in group_quotes
            if quote.total_fare is not None
        ]

        bounds = calculate_outlier_bounds(
            values
        )

        for quote in group_quotes:
            is_outlier = False

            if (
                bounds is not None
                and quote.total_fare is not None
            ):
                lower_bound, upper_bound = bounds

                is_outlier = (
                    quote.total_fare < lower_bound
                    or quote.total_fare > upper_bound
                )

            quote.is_outlier = is_outlier

            if is_outlier:
                outliers += 1
            else:
                quote.is_clean = True
                cleaned += 1

    db.commit()

    return {
        "processed": processed,
        "cleaned": cleaned,
        "outliers": outliers,
        "rejected": rejected,
    }
