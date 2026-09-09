from sqlalchemy import inspect

from app.db.base import Base
from app.db.session import engine

import app.models  # noqa: F401


def init_database():
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("Database initialized successfully.")
    print("Created tables:")

    for table in tables:
        print(f" - {table}")


if __name__ == "__main__":
    init_database()