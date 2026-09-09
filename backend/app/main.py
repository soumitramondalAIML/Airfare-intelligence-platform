from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.scrapers import router as scraper_router
from app.api.routes.data_quality import router as data_quality_router
from app.api.routes.fares import router as fares_router
from app.api.routes.health import router as health_router
from app.api.routes.index import router as index_router
from app.api.routes.reference import router as reference_router
from app.api.routes.quality import router as quality_router
from app.api.routes.backtest import router as backtest_router
from app.api.routes.references import router as references_router
from app.core.config import settings
from app.db.init_db import init_database
from app.db.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    init_database()

    print("Seeding database...")
    seed_database()

    print("Database initialization completed.")

    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for the Real-time "
        "Airfare Price Index for India"
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    reference_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    fares_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    scraper_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    data_quality_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    index_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    quality_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    backtest_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    references_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
    }