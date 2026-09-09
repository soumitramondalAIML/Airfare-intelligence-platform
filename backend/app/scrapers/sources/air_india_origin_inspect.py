from playwright.sync_api import sync_playwright


URL = (
    "https://www.airindia.com/en-in/"
    "book-flights/delhi-to-mumbai-flights"
)


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def inspect_origin_popup():
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(
            headless=False,
        )

        context = browser.new_context(
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            viewport={
                "width": 1440,
                "height": 1000,
            },
        )

        page = context.new_page()

        print("Opening Air India...")

        page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(6000)

        # Close cookie banner if it appears.
        try:
            accept_button = page.get_by_role(
                "button",
                name="Accept All",
            ).first

            if accept_button.is_visible():
                accept_button.click()
                page.wait_for_timeout(1000)

                print(
                    "Cookie banner accepted."
                )

        except Exception:
            print(
                "No cookie banner needed."
            )

        print()
        print("Clicking FROM...")

        from_button = page.get_by_role(
            "button",
            name="FROM",
            exact=True,
        )

        from_button.click()

        page.wait_for_timeout(1500)

        print()
        print(
            "========== INPUTS AFTER FROM =========="
        )

        inputs = page.locator("input")

        print(
            "Input count:",
            inputs.count(),
        )

        for index in range(
            inputs.count()
        ):
            element = inputs.nth(index)

            try:
                print()
                print(
                    f"INPUT #{index}"
                )

                print(
                    " type:",
                    clean(
                        element.get_attribute(
                            "type"
                        )
                    ),
                )

                print(
                    " name:",
                    clean(
                        element.get_attribute(
                            "name"
                        )
                    ),
                )

                print(
                    " id:",
                    clean(
                        element.get_attribute(
                            "id"
                        )
                    ),
                )

                print(
                    " placeholder:",
                    clean(
                        element.get_attribute(
                            "placeholder"
                        )
                    ),
                )

                print(
                    " aria-label:",
                    clean(
                        element.get_attribute(
                            "aria-label"
                        )
                    ),
                )

                print(
                    " role:",
                    clean(
                        element.get_attribute(
                            "role"
                        )
                    ),
                )

            except Exception:
                pass

        print()
        print(
            "========== BUTTONS AFTER FROM =========="
        )

        buttons = page.locator("button")

        for index in range(
            buttons.count()
        ):
            button = buttons.nth(index)

            try:
                text = clean(
                    button.inner_text()
                )

                aria = clean(
                    button.get_attribute(
                        "aria-label"
                    )
                )

                if text or aria:
                    if any(
                        word in (
                            text + " " + aria
                        ).upper()
                        for word in [
                            "DELHI",
                            "DEL",
                            "AIRPORT",
                            "RECENT",
                            "POPULAR",
                            "CLOSE",
                        ]
                    ):
                        print()
                        print(
                            f"BUTTON #{index}"
                        )
                        print(
                            " text:",
                            text[:300],
                        )
                        print(
                            " aria-label:",
                            aria,
                        )

            except Exception:
                pass

        print()
        print(
            "========== POPUP TEXT =========="
        )

        body_lines = [
            line.strip()
            for line in page.locator(
                "body"
            ).inner_text().splitlines()
            if line.strip()
        ]

        for index, line in enumerate(
            body_lines
        ):
            upper_line = line.upper()

            if any(
                keyword in upper_line
                for keyword in [
                    "DELHI",
                    "AIRPORT",
                    "SEARCH",
                    "POPULAR",
                    "RECENT",
                ]
            ):
                start = max(
                    0,
                    index - 2,
                )

                end = min(
                    len(body_lines),
                    index + 5,
                )

                print()
                print(
                    f"--- Around line {index} ---"
                )

                for nearby in body_lines[
                    start:end
                ]:
                    print(nearby)

        print()
        print(
            "Origin popup inspection complete."
        )

        input(
            "Press Enter to close browser..."
        )

        browser.close()


if __name__ == "__main__":
    inspect_origin_popup()