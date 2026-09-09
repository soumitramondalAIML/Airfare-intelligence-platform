from playwright.sync_api import sync_playwright


URL = (
    "https://www.airindia.com/en-in/"
    "book-flights/delhi-to-mumbai-flights"
)


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def debug_origin():
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

        # Close cookie banner if visible.
        try:
            accept = page.get_by_role(
                "button",
                name="Accept All",
            ).first

            if accept.is_visible():
                accept.click()
                page.wait_for_timeout(1000)
                print("Cookie banner closed.")
        except Exception:
            pass

        print()
        print("Clicking FROM...")

        page.get_by_role(
            "button",
            name="FROM",
            exact=True,
        ).click()

        page.wait_for_timeout(1500)

        print()
        print(
            "========== VISIBLE INPUTS =========="
        )

        inputs = page.locator(
            "input:visible"
        )

        print(
            "Visible input count:",
            inputs.count(),
        )

        for i in range(inputs.count()):
            element = inputs.nth(i)

            print()
            print(f"INPUT #{i}")

            for attr in [
                "type",
                "name",
                "id",
                "placeholder",
                "aria-label",
                "role",
                "autocomplete",
            ]:
                print(
                    f" {attr}:",
                    clean(
                        element.get_attribute(
                            attr
                        )
                    ),
                )

        print()
        print(
            "========== VISIBLE DIALOGS =========="
        )

        dialogs = page.locator(
            '[role="dialog"]:visible'
        )

        print(
            "Dialog count:",
            dialogs.count(),
        )

        for i in range(dialogs.count()):
            dialog = dialogs.nth(i)

            print()
            print(f"DIALOG #{i}")

            try:
                text = dialog.inner_text()
                print(text[:2000])
            except Exception:
                pass

        print()
        print(
            "========== VISIBLE LISTBOXES =========="
        )

        listboxes = page.locator(
            '[role="listbox"]:visible'
        )

        print(
            "Listbox count:",
            listboxes.count(),
        )

        for i in range(
            listboxes.count()
        ):
            listbox = listboxes.nth(i)

            print()
            print(f"LISTBOX #{i}")

            try:
                print(
                    listbox.inner_text()[:2000]
                )
            except Exception:
                pass

        print()
        print(
            "========== VISIBLE OPTIONS =========="
        )

        options = page.locator(
            '[role="option"]:visible'
        )

        print(
            "Option count:",
            options.count(),
        )

        for i in range(
            min(options.count(), 20)
        ):
            option = options.nth(i)

            try:
                print(
                    f"OPTION #{i}:",
                    clean(
                        option.inner_text()
                    ),
                )
            except Exception:
                pass

        print()
        print(
            "========== ACTIVE ELEMENT =========="
        )

        try:
            active_html = page.evaluate(
                "() => document.activeElement.outerHTML"
            )

            print(
                active_html[:3000]
            )
        except Exception as exc:
            print(
                "Could not inspect active element:",
                exc,
            )

        print()
        print(
            "========== CONTENTEDITABLE =========="
        )

        editable = page.locator(
            '[contenteditable="true"]:visible'
        )

        print(
            "Contenteditable count:",
            editable.count(),
        )

        for i in range(
            editable.count()
        ):
            element = editable.nth(i)

            try:
                print(
                    element.evaluate(
                        "el => el.outerHTML"
                    )[:1500]
                )
            except Exception:
                pass

        print()
        print(
            "Origin debug complete."
        )

        input(
            "Press Enter to close browser..."
        )

        browser.close()


if __name__ == "__main__":
    debug_origin()