from playwright.sync_api import sync_playwright


URL = (
    "https://www.airindia.com/en-us/"
    "book-flights/delhi-to-mumbai-flights"
)


def inspect_calendar():
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(
            headless=False,
        )

        context = browser.new_context(
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            viewport={
                "width": 1440,
                "height": 1100,
            },
        )

        page = context.new_page()

        print("Opening Air India...")

        page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(7000)

        # Close cookie banner if present.
        try:
            accept = page.get_by_role(
                "button",
                name="Accept All",
            ).first

            if accept.is_visible():
                accept.click()
                page.wait_for_timeout(1000)

        except Exception:
            pass

        print()
        print(
            "========== CALENDAR HEADING =========="
        )

        heading = page.get_by_text(
            "When to fly from Delhi to Mumbai?",
            exact=True,
        )

        print(
            "Heading count:",
            heading.count(),
        )

        print()
        print(
            "========== MONTH ELEMENTS =========="
        )

        month_elements = page.locator(
            "body *"
        ).evaluate_all(
            """
            elements => elements
                .filter(el => {
                    const text =
                        (el.textContent || "").trim();

                    const visible =
                        el.getClientRects().length > 0;

                    return (
                        visible &&
                        /^(SEP|OCT|NOV|DEC) 2026$/.test(text)
                    );
                })
                .slice(0, 30)
                .map(el => ({
                    tag: el.tagName,
                    text: (el.textContent || "").trim(),
                    className: el.className,
                    role: el.getAttribute("role"),
                    ariaLabel: el.getAttribute("aria-label"),
                    title: el.getAttribute("title"),
                    outerHTML: el.outerHTML.slice(0, 1500)
                }))
            """
        )

        for index, item in enumerate(
            month_elements
        ):
            print()
            print(
                f"MONTH #{index}"
            )

            for key, value in item.items():
                print(
                    f"{key}:",
                    value,
                )

        print()
        print(
            "========== DAILY FARE ELEMENTS =========="
        )

        fare_elements = page.locator(
            "body *"
        ).evaluate_all(
            """
            elements => elements
                .filter(el => {
                    const text =
                        (el.textContent || "")
                            .replace(/\\s+/g, " ")
                            .trim();

                    const visible =
                        el.getClientRects().length > 0;

                    return (
                        visible &&
                        /^INR\\s*[0-9.,]+[Kk]?$/.test(text)
                    );
                })
                .slice(0, 100)
                .map(el => ({
                    tag: el.tagName,
                    text: (el.textContent || "")
                        .replace(/\\s+/g, " ")
                        .trim(),

                    className: el.className,

                    role: el.getAttribute("role"),

                    ariaLabel:
                        el.getAttribute("aria-label"),

                    title:
                        el.getAttribute("title"),

                    value:
                        el.getAttribute("value"),

                    dataValue:
                        el.getAttribute("data-value"),

                    dataPrice:
                        el.getAttribute("data-price"),

                    dataFare:
                        el.getAttribute("data-fare"),

                    parentHTML:
                        el.parentElement
                            ? el.parentElement.outerHTML.slice(
                                0,
                                2500
                            )
                            : "",

                    outerHTML:
                        el.outerHTML.slice(
                            0,
                            1500
                        )
                }))
            """
        )

        print(
            "Fare element count:",
            len(fare_elements),
        )

        for index, item in enumerate(
            fare_elements[:15]
        ):
            print()
            print(
                f"FARE #{index}"
            )

            for key, value in item.items():
                print(
                    f"{key}:",
                    value,
                )

        print()
        print(
            "========== DATE 5 ELEMENTS =========="
        )

        date_elements = page.locator(
            "body *"
        ).evaluate_all(
            """
            elements => elements
                .filter(el => {
                    const text =
                        (el.textContent || "").trim();

                    const visible =
                        el.getClientRects().length > 0;

                    return (
                        visible &&
                        text === "5"
                    );
                })
                .slice(0, 30)
                .map(el => ({
                    tag: el.tagName,
                    className: el.className,
                    role: el.getAttribute("role"),
                    ariaLabel:
                        el.getAttribute("aria-label"),
                    title:
                        el.getAttribute("title"),
                    parentHTML:
                        el.parentElement
                            ? el.parentElement.outerHTML.slice(
                                0,
                                3000
                            )
                            : ""
                }))
            """
        )

        for index, item in enumerate(
            date_elements
        ):
            print()
            print(
                f"DATE-5 #{index}"
            )

            for key, value in item.items():
                print(
                    f"{key}:",
                    value,
                )

        print()
        print(
            "Calendar inspection complete."
        )

        input(
            "Press Enter to close browser..."
        )

        browser.close()


if __name__ == "__main__":
    inspect_calendar()