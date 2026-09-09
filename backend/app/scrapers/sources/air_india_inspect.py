from playwright.sync_api import sync_playwright


URL = (
    "https://www.airindia.com/en-us/"
    "book-flights/delhi-to-mumbai-flights"
)


def inspect_air_india():
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(
            headless=True,
        )

        context = browser.new_context(
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )

        page = context.new_page()

        print("Opening Air India...")
        print(URL)

        page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(8000)

        print()
        print("Page title:")
        print(page.title())

        print()
        print("Final URL:")
        print(page.url)

        body_text = page.locator(
            "body"
        ).inner_text()

        lines = [
            line.strip()
            for line in body_text.splitlines()
            if line.strip()
        ]

        keywords = [
            "When to fly",
            "Best Price",
            "Today's Rate",
            "SEP 2026",
            "OCT 2026",
            "NOV 2026",
            "INR",
            "48hrs",
            "Economy Class",
        ]

        print()
        print(
            "========== RELEVANT PAGE TEXT =========="
        )

        for index, line in enumerate(lines):
            upper_line = line.upper()

            if any(
                keyword.upper() in upper_line
                for keyword in keywords
            ):
                start = max(
                    0,
                    index - 3,
                )

                end = min(
                    len(lines),
                    index + 8,
                )

                print()
                print(
                    f"--- Around line {index} ---"
                )

                for nearby in lines[
                    start:end
                ]:
                    print(nearby)

        print()
        print(
            "========== END =========="
        )

        browser.close()


if __name__ == "__main__":
    inspect_air_india()