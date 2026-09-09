from playwright.sync_api import sync_playwright


URL = (
    "https://www.airindia.com/en-in/"
    "book-flights/delhi-to-mumbai-flights"
)


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def inspect_from_structure():
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

        page.wait_for_timeout(7000)

        # Cookie banner
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

        from_button = page.get_by_role(
            "button",
            name="FROM",
            exact=True,
        )

        print()
        print(
            "========== FROM BUTTON =========="
        )

        print(
            from_button.evaluate(
                "el => el.outerHTML"
            )
        )

        print()
        print(
            "========== PARENT BEFORE CLICK =========="
        )

        print(
            from_button.evaluate(
                "el => el.parentElement.outerHTML"
            )[:5000]
        )

        text_before = page.locator(
            "body"
        ).inner_text()

        print()
        print("Clicking FROM...")

        from_button.click()

        page.wait_for_timeout(2500)

        text_after = page.locator(
            "body"
        ).inner_text()

        print()
        print(
            "Body text changed:",
            text_before != text_after,
        )

        print()
        print(
            "========== BUTTON AFTER CLICK =========="
        )

        print(
            from_button.evaluate(
                "el => el.outerHTML"
            )
        )

        print()
        print(
            "========== PARENT AFTER CLICK =========="
        )

        print(
            from_button.evaluate(
                "el => el.parentElement.outerHTML"
            )[:8000]
        )

        print()
        print(
            "========== IFRAMES =========="
        )

        print(
            "Frame count:",
            len(page.frames),
        )

        for index, frame in enumerate(
            page.frames
        ):
            print()
            print(
                f"FRAME #{index}"
            )
            print(
                "URL:",
                frame.url,
            )

            try:
                visible_inputs = frame.locator(
                    "input:visible"
                )

                print(
                    "Visible inputs:",
                    visible_inputs.count(),
                )

                for i in range(
                    visible_inputs.count()
                ):
                    element = visible_inputs.nth(i)

                    print(
                        " ",
                        i,
                        "placeholder=",
                        clean(
                            element.get_attribute(
                                "placeholder"
                            )
                        ),
                        "aria-label=",
                        clean(
                            element.get_attribute(
                                "aria-label"
                            )
                        ),
                    )

            except Exception as exc:
                print(
                    "Unable to inspect frame:",
                    exc,
                )

        print()
        print(
            "========== VISIBLE TEXTBOX ROLES =========="
        )

        textboxes = page.get_by_role(
            "textbox"
        )

        print(
            "Textbox count:",
            textboxes.count(),
        )

        for i in range(
            textboxes.count()
        ):
            textbox = textboxes.nth(i)

            try:
                if textbox.is_visible():
                    print()
                    print(
                        f"TEXTBOX #{i}"
                    )
                    print(
                        textbox.evaluate(
                            "el => el.outerHTML"
                        )[:2000]
                    )
            except Exception:
                pass

        print()
        print(
            "========== FIXED ELEMENTS =========="
        )

        fixed_elements = page.locator(
            "*"
        ).evaluate_all(
            """
            elements => elements
                .filter(el => {
                    const style =
                        window.getComputedStyle(el);

                    return (
                        style.position === "fixed" &&
                        style.display !== "none" &&
                        style.visibility !== "hidden"
                    );
                })
                .slice(0, 30)
                .map(el => el.outerHTML.slice(0, 1500))
            """
        )

        print(
            "Visible fixed elements:",
            len(fixed_elements),
        )

        for index, html in enumerate(
            fixed_elements
        ):
            print()
            print(
                f"FIXED #{index}"
            )
            print(html)

        print()
        print(
            "Inspection complete."
        )

        input(
            "Press Enter to close browser..."
        )

        browser.close()


if __name__ == "__main__":
    inspect_from_structure()