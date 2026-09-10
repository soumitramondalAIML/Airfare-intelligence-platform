import re
import time
import os

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from playwright.sync_api import (
    Page,
    sync_playwright,
)


# India Standard Time
IST = timezone(
    timedelta(
        hours=5,
        minutes=30,
    )
)


# Required advance-purchase windows
ADVANCE_WINDOWS = [
    1,
    7,
    15,
    30,
    45,
]


# Representative routes
ROUTES = [
    {
        "origin": "DEL",
        "destination": "BOM",
        "name": "Delhi to Mumbai",
        "slug": "delhi-to-mumbai-flights",
    },
    {
        "origin": "DEL",
        "destination": "BLR",
        "name": "Delhi to Bangalore",
        "slug": "delhi-to-bangalore-flights",
    },
    {
        "origin": "BOM",
        "destination": "BLR",
        "name": "Mumbai to Bangalore",
        "slug": "mumbai-to-bangalore-flights",
    },
    {
        "origin": "DEL",
        "destination": "CCU",
        "name": "Delhi to Kolkata",
        "slug": "delhi-to-kolkata-flights",
    },
    {
        "origin": "BLR",
        "destination": "HYD",
        "name": "Bangalore to Hyderabad",
        "slug": "bangalore-to-hyderabad-flights",
    },
    {
        "origin": "MAA",
        "destination": "DEL",
        "name": "Chennai to Delhi",
        "slug": "chennai-to-delhi-flights",
    },
]


def build_route_urls(
    route: dict,
) -> list[str]:
    """
    Try the US locale first because its
    fare calendar has been rendering more
    consistently.

    If that fails, automatically try the
    Indian locale.
    """

    slug = route["slug"]

    return [
        (
            "https://www.airindia.com/"
            "en-us/book-flights/"
            f"{slug}"
        ),
        (
            "https://www.airindia.com/"
            "en-in/book-flights/"
            f"{slug}"
        ),
    ]


def month_label(
    target_date,
) -> str:
    """
    Convert a date such as 2026-09-05
    into Air India's month label:

    SEP 2026
    """

    return target_date.strftime(
        "%b %Y"
    ).upper()


def extract_price(
    aria_label,
):
    """
    Example aria-label:

    2026-09-05: INR 6,610

    Returns:

    6610.0
    """

    if not aria_label:
        return None

    match = re.search(
        r"INR\s*([\d,]+)",
        aria_label,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    price_text = (
        match.group(1)
        .replace(
            ",",
            "",
        )
    )

    try:
        return float(
            price_text
        )

    except ValueError:
        return None


def close_cookie_banner(
    page: Page,
):
    """
    Close Air India's cookie banner
    when it appears.
    """

    try:
        accept_button = (
            page.get_by_role(
                "button",
                name="Accept All",
            ).first
        )

        if (
            accept_button.is_visible()
        ):
            accept_button.click()

            page.wait_for_timeout(
                700
            )

    except Exception:
        pass


def wait_for_calendar(
    page: Page,
) -> bool:
    """
    Wait for the 'When to fly from...'
    fare-calendar section.

    Air India's heading sometimes appears
    before the month/date cells finish
    rendering, so an additional wait is
    intentionally used.
    """

    try:
        heading = (
            page.get_by_text(
                re.compile(
                    r"When to fly from",
                    re.IGNORECASE,
                )
            ).first
        )

        heading.wait_for(
            state="visible",
            timeout=15000,
        )

        # Allow React/JavaScript calendar
        # components to finish hydrating.
        page.wait_for_timeout(
            5000
        )

        return True

    except Exception:
        return False


def select_month(
    page: Page,
    target_date,
) -> bool:
    """
    Select the required month.

    Air India's month label is often a DIV
    inside another clickable element, so
    we locate the exact text and click the
    nearest clickable parent using DOM JS.
    """

    label = month_label(
        target_date
    )

    print(
        f"Switching calendar to "
        f"{label}..."
    )

    for attempt in range(
        1,
        4,
    ):
        try:
            clicked = page.evaluate(
                """
                (label) => {
                    const elements = [
                        ...document.querySelectorAll(
                            "body *"
                        )
                    ];

                    const matches =
                        elements.filter(
                            el =>
                                (
                                    el.textContent ||
                                    ""
                                ).trim() === label
                        );

                    for (
                        const element
                        of matches
                    ) {
                        const rect =
                            element
                                .getBoundingClientRect();

                        if (
                            rect.width <= 0 ||
                            rect.height <= 0
                        ) {
                            continue;
                        }

                        const clickable =
                            element.closest(
                                "button"
                            ) ||
                            element.closest(
                                '[role="button"]'
                            ) ||
                            element;

                        clickable
                            .scrollIntoView({
                                block: "center",
                                inline: "center"
                            });

                        clickable.click();

                        return true;
                    }

                    return false;
                }
                """,
                label,
            )

            if clicked:
                page.wait_for_timeout(
                    2500
                )

                return True

        except Exception as exc:
            print(
                f"Month switch attempt "
                f"{attempt} failed:",
                exc,
            )

        page.wait_for_timeout(
            1500
        )

    print(
        f"Unable to switch to "
        f"{label}."
    )

    return False

      


def find_fare(
    page: Page,
    target_date,
):
    """
    Find the exact Air India fare for
    one departure date.

    We use the aria-label rather than
    visible text because visible text
    may show:

        INR 6.6K

    while aria-label contains:

        2026-09-05: INR 6,610
    """

    date_text = (
        target_date.isoformat()
    )

    selector = (
        'button[aria-label^="'
        + date_text
        + ': INR"]'
    )

    fare_button = (
        page.locator(
            selector
        ).first
    )

    try:
        fare_button.wait_for(
            state="visible",
            timeout=4000,
        )

    except Exception:
        return None

    try:
        aria_label = (
            fare_button.get_attribute(
                "aria-label"
            )
        )

        price = extract_price(
            aria_label
        )

        if price is None:
            return None

        return {
            "departure_date":
                date_text,

            "total_fare":
                price,

            "raw_label":
                aria_label,
        }

    except Exception:
        return None


def open_route_page(
    page: Page,
    route: dict,
):
    """
    Try both Air India locales.

    Each locale gets two attempts because
    the fare-calendar component sometimes
    fails to hydrate on the first load.
    """

    urls = build_route_urls(
        route
    )

    for url in urls:
        for attempt in range(
            1,
            3,
        ):
            print(
                f"Trying: {url} "
                f"(attempt {attempt}/2)"
            )

            try:
                page.goto(
                    url,
                    wait_until=(
                        "domcontentloaded"
                    ),
                    timeout=60000,
                )

            except Exception as exc:
                print(
                    "Page load failed:",
                    exc,
                )

                continue

            close_cookie_banner(
                page
            )

            calendar_ready = (
                wait_for_calendar(
                    page
                )
            )

            if calendar_ready:
                print(
                    "Fare calendar found."
                )

                return url

            print(
                "Fare calendar not found "
                "on this attempt."
            )

            page.wait_for_timeout(
                2000
            )

    return None

      


def collect_route(
    page: Page,
    route: dict,
    collection_date,
):
    """
    Collect T+1, T+7, T+15,
    T+30 and T+45 fares for one route.
    """

    print()
    print(
        "=" * 60
    )

    print(
        f"{route['origin']} "
        f"-> "
        f"{route['destination']}"
    )

    print(
        "=" * 60
    )

    source_url = (
        open_route_page(
            page,
            route,
        )
    )

    if source_url is None:
        print(
            "Fare calendar heading "
            "not found on either locale."
        )

        return []

    results = []

    for advance_days in (
        ADVANCE_WINDOWS
    ):
        target_date = (
            collection_date
            + timedelta(
                days=advance_days
            )
        )

        # First try the currently
        # displayed calendar.
        fare = find_fare(
            page,
            target_date,
        )

        # If the requested date is not
        # visible, switch to its month.
        if fare is None:
            month_ready = (
                select_month(
                    page,
                    target_date,
                )
            )

            if not month_ready:
                print(
                    f"T+{advance_days:<2} "
                    f"{target_date} "
                    "-> MONTH NOT FOUND"
                )

                continue

            # Try again after the
            # calendar has changed month.
            fare = find_fare(
                page,
                target_date,
            )

        if fare is None:
            print(
                f"T+{advance_days:<2} "
                f"{target_date} "
                "-> FARE NOT FOUND"
            )

            continue

        observation = {
            "origin":
                route[
                    "origin"
                ],

            "destination":
                route[
                    "destination"
                ],

            "route":
                (
                    f"{route['origin']}-"
                    f"{route['destination']}"
                ),

            "carrier":
                "Air India",

            "carrier_code":
                "AI",

            "source":
                "Air India",

            "source_type":
                "airline",

            "collection_method":
                "route_fare_calendar",

            "collected_at":
                datetime.now(
                    IST
                ).isoformat(),

            "departure_date":
                fare[
                    "departure_date"
                ],

            "advance_purchase_days":
                advance_days,

            "purchase_window":
                f"T+{advance_days}",

            "fare_class":
                "Economy",

            # Air India's calendar does
            # not expose a trustworthy
            # component-level breakdown.
            "base_fare":
                None,

            "taxes":
                None,

            "user_development_fee":
                None,

            "convenience_fee":
                None,

            "total_fare":
                fare[
                    "total_fare"
                ],

            "currency":
                "INR",

            "availability_status":
                "available",

            "freshness_note":
                (
                    "Air India states "
                    "calendar fares were "
                    "collected within the "
                    "last 48 hours."
                ),

            "source_url":
                source_url,

            "raw_label":
                fare[
                    "raw_label"
                ],
        }

        results.append(
            observation
        )

        print(
            f"T+{advance_days:<2} "
            f"{target_date} "
            f"-> INR "
            f"{fare['total_fare']:,.0f}"
        )

    return results


def collect_air_india():
    """
    Run the full Air India collection.

    6 routes × 5 purchase windows
    = maximum 30 observations.
    """

    collection_time = (
        datetime.now(
            IST
        )
    )

    collection_date = (
        collection_time.date()
    )

    print()
    print(
        "AIR INDIA REAL FARE "
        "COLLECTION"
    )

    print(
        "Collection date:",
        collection_date,
    )

    print(
        "Advance windows:",
        ADVANCE_WINDOWS,
    )

    all_results = []

    with sync_playwright() as (
        playwright
    ):
        headless = (
           os.getenv(
               "PLAYWRIGHT_HEADLESS",
               "false",
            ).lower()
            == "true"
       )

        browser = (
           playwright.firefox.launch(
               headless=headless,
         )
        )

        context = (
            browser.new_context(
                locale="en-IN",
                timezone_id=(
                    "Asia/Kolkata"
                ),
                viewport={
                    "width":
                        1440,

                    "height":
                        1000,
                },
            )
        )

        for index, route in enumerate(
            ROUTES
        ):
            # Fresh page for every route.
            # This prevents state from the
            # previous calendar leaking
            # into the next route.
            page = (
                context.new_page()
            )

            try:
                route_results = (
                    collect_route(
                        page,
                        route,
                        collection_date,
                    )
                )

                all_results.extend(
                    route_results
                )

            except Exception as exc:
                print(
                    "Unexpected route "
                    "collection error:",
                    exc,
                )

            finally:
                try:
                    page.close()
                except Exception:
                    pass

            # Ethical throttling:
            # wait between route pages.
            if index < (
                len(ROUTES) - 1
            ):
                print()
                print(
                    "Waiting before "
                    "next route..."
                )

                time.sleep(
                    3
                )

        browser.close()

    print()
    print(
        "=" * 60
    )

    print(
        "COLLECTION SUMMARY"
    )

    print(
        "=" * 60
    )

    expected_observations = (
        len(ROUTES)
        * len(
            ADVANCE_WINDOWS
        )
    )

    collected_observations = (
        len(
            all_results
        )
    )

    missing_observations = (
        expected_observations
        - collected_observations
    )

    print(
        "Expected observations:",
        expected_observations,
    )

    print(
        "Collected observations:",
        collected_observations,
    )

    print(
        "Missing observations:",
        missing_observations,
    )

    if expected_observations:
        coverage = (
            collected_observations
            / expected_observations
            * 100
        )

    else:
        coverage = 0

    print(
        "Coverage:",
        f"{coverage:.1f}%",
    )

    print()
    print(
        "RESULTS"
    )

    for item in all_results:
        print(
            f"{item['route']} "
            f"{item['purchase_window']} "
            f"{item['departure_date']} "
            f"INR "
            f"{item['total_fare']:,.0f}"
        )

    return all_results


if __name__ == "__main__":
    collect_air_india()