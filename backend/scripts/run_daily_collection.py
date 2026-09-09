import sys
from pathlib import Path

# Add the backend directory to Python's import path.
BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from datetime import datetime

from app.db.session import SessionLocal
from app.services.scraping.air_india_ingestion import (
    run_air_india_ingestion,
)
from app.services.index.price_index import (
    rebuild_price_index_history,
)


def main():
    print("=" * 70)
    print("AIRFARE PRICE INDEX - DAILY UPDATE")
    print("=" * 70)
    print(
        f"Started at: "
        f"{datetime.now().isoformat()}"
    )
    print()

    # ---------------------------------------------------------
    # 1. Collect real Air India observations
    # ---------------------------------------------------------
    print("[1/4] Collecting Air India fares...")
    print()

    ingestion_result = (
        run_air_india_ingestion()
    )

    print()
    print("Air India ingestion result:")
    print(ingestion_result)
    print()

    # ---------------------------------------------------------
    # 2. Rebuild daily index history
    # ---------------------------------------------------------
    print("[2/4] Rebuilding DAILY index...")

    db = SessionLocal()

    try:
        daily_result = (
            rebuild_price_index_history(
                db,
                frequency="daily",
            )
        )

        print()
        print("Daily index result:")
        print(daily_result)

        # -----------------------------------------------------
        # 3. Rebuild weekly index history
        # -----------------------------------------------------
        print()
        print("[3/4] Rebuilding WEEKLY index...")

        weekly_result = (
            rebuild_price_index_history(
                db,
                frequency="weekly",
            )
        )

        print()
        print("Weekly index result:")
        print(weekly_result)

        # -----------------------------------------------------
        # 4. Rebuild monthly index history
        # -----------------------------------------------------
        print()
        print("[4/4] Rebuilding MONTHLY index...")

        monthly_result = (
            rebuild_price_index_history(
                db,
                frequency="monthly",
            )
        )

        print()
        print("Monthly index result:")
        print(monthly_result)

    finally:
        db.close()

    print()
    print("=" * 70)
    print("DAILY UPDATE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()