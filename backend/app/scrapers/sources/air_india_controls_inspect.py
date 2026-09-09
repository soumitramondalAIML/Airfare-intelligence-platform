from playwright.sync_api import sync_playwright


URL = (
    "https://www.airindia.com/en-in/"
    "book-flights/delhi-to-mumbai-flights"
)


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def inspect_controls():
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

        page.wait_for_timeout(8000)

        print()
        print("TITLE:")
        print(page.title())

        print()
        print(
            "========== INPUTS =========="
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
                    " value:",
                    clean(
                        element.input_value()
                    ),
                )

            except Exception as exc:
                print(
                    " unable to inspect:",
                    exc,
                )

        print()
        print(
            "========== BUTTONS =========="
        )

        buttons = page.locator("button")

        print(
            "Button count:",
            buttons.count(),
        )

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

                title = clean(
                    button.get_attribute(
                        "title"
                    )
                )

                if (
                    text
                    or aria
                    or title
                ):
                    print()
                    print(
                        f"BUTTON #{index}"
                    )
                    print(
                        " text:",
                        text[:200],
                    )
                    print(
                        " aria-label:",
                        aria,
                    )
                    print(
                        " title:",
                        title,
                    )

            except Exception:
                pass

        print()
        print(
            "========== SELECTS =========="
        )

        selects = page.locator("select")

        print(
            "Select count:",
            selects.count(),
        )

        for index in range(
            selects.count()
        ):
            select = selects.nth(index)

            try:
                print()
                print(
                    f"SELECT #{index}"
                )

                print(
                    " name:",
                    clean(
                        select.get_attribute(
                            "name"
                        )
                    ),
                )

                print(
                    " id:",
                    clean(
                        select.get_attribute(
                            "id"
                        )
                    ),
                )

                print(
                    " aria-label:",
                    clean(
                        select.get_attribute(
                            "aria-label"
                        )
                    ),
                )

            except Exception:
                pass

        print()
        print(
            "========== COMBOBOXES =========="
        )

        combos = page.get_by_role(
            "combobox"
        )

        print(
            "Combobox count:",
            combos.count(),
        )

        for index in range(
            combos.count()
        ):
            combo = combos.nth(index)

            try:
                print()
                print(
                    f"COMBOBOX #{index}"
                )

                print(
                    " placeholder:",
                    clean(
                        combo.get_attribute(
                            "placeholder"
                        )
                    ),
                )

                print(
                    " aria-label:",
                    clean(
                        combo.get_attribute(
                            "aria-label"
                        )
                    ),
                )

                print(
                    " value:",
                    clean(
                        combo.input_value()
                    ),
                )

            except Exception:
                pass

        print()
        print(
            "========== BOOKING TEXT =========="
        )

        body_lines = [
            line.strip()
            for line in page.locator(
                "body"
            ).inner_text().splitlines()
            if line.strip()
        ]

        keywords = {
            "FROM",
            "TO",
            "DEPART",
            "RETURN",
            "PASSENGER",
            "CLASS",
            "SEARCH",
            "ONE WAY",
        }

        for index, line in enumerate(
            body_lines
        ):
            if (
                line.upper()
                in keywords
            ):
                print()
                print(
                    f"--- Around {index} ---"
                )

                start = max(
                    0,
                    index - 2,
                )

                end = min(
                    len(body_lines),
                    index + 5,
                )

                for nearby in body_lines[
                    start:end
                ]:
                    print(nearby)

        print()
        print(
            "Inspection finished."
        )

        input(
            "Press Enter to close browser..."
        )

        browser.close()


if __name__ == "__main__":
    inspect_controls()