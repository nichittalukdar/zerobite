from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api.routes import auth, claims, deliveries, donations, matching, notifications, users
from app.core.config import settings
from app.core.database import Base, engine
import app.models  # noqa: F401 - registers SQLAlchemy models with metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables for local development; production schema changes use Alembic.
    if settings.environment.lower() not in {"production", "prod"}:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Zerobite API",
    version=settings.app_version,
    description=(
        "Zerobite connects surplus-food donors with receivers "
        "through secure APIs, delivery tracking, and transparent "
        "rule-based matching."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(donations.router, prefix="/api/donations", tags=["Donations"])
app.include_router(claims.router, prefix="/api/claims", tags=["Claims"])
app.include_router(matching.router, prefix="/api", tags=["AI Matching"])
app.include_router(deliveries.router, prefix="/api/deliveries", tags=["Deliveries"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


@app.get("/", tags=["System"])
def root():
    return {"project": "Zerobite", "message": "Turn Extra Food Into Extra Hope", "developer": settings.developer_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy", "service": "Zerobite Backend"}


@app.get("/health/ready", tags=["System"])
def readiness():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
