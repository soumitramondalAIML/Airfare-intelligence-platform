from datetime import date, timedelta

from app.scrapers.base import ScrapedFare


class MockAirfareScraper:
    source_code = "makemytrip"

    def scrape(self) -> list[ScrapedFare]:
        today = date.today()

        return [
            ScrapedFare(
                origin="DEL",
                destination="BOM",
                carrier_code="6E",
                source_code=self.source_code,
                departure_date=today + timedelta(days=7),
                advance_purchase_days=7,
                fare_class="Economy",
                base_fare=4300,
                taxes=700,
                user_development_fee=150,
                convenience_fee=300,
                total_fare=5450,
            ),
            ScrapedFare(
                origin="DEL",
                destination="BLR",
                carrier_code="AI",
                source_code=self.source_code,
                departure_date=today + timedelta(days=15),
                advance_purchase_days=15,
                fare_class="Economy",
                base_fare=5200,
                taxes=800,
                user_development_fee=150,
                convenience_fee=300,
                total_fare=6450,
            ),
            ScrapedFare(
                origin="BOM",
                destination="BLR",
                carrier_code="QP",
                source_code=self.source_code,
                departure_date=today + timedelta(days=30),
                advance_purchase_days=30,
                fare_class="Economy",
                base_fare=3400,
                taxes=550,
                user_development_fee=100,
                convenience_fee=250,
                total_fare=4300,
            ),
            ScrapedFare(
                origin="DEL",
                destination="CCU",
                carrier_code="6E",
                source_code=self.source_code,
                departure_date=today + timedelta(days=7),
                advance_purchase_days=7,
                fare_class="Economy",
                base_fare=4700,
                taxes=750,
                user_development_fee=150,
                convenience_fee=300,
                total_fare=5900,
            ),
            ScrapedFare(
                origin="BLR",
                destination="HYD",
                carrier_code="IX",
                source_code=self.source_code,
                departure_date=today + timedelta(days=1),
                advance_purchase_days=1,
                fare_class="Economy",
                base_fare=2400,
                taxes=500,
                user_development_fee=100,
                convenience_fee=200,
                total_fare=3200,
            ),
        ]