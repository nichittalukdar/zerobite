"""Create harmless local demo users. All demo passwords are intentionally disposable."""
import os
import sys
from pathlib import Path
from sqlalchemy import select
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)
from app.core.config import settings  # noqa: E402
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import User  # noqa: E402


def main():
    if settings.environment.lower() in {"production", "prod"}:
        raise SystemExit("Demo seeding is disabled in production.")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users = [
            ("Demo Donor", "donor.demo@example.com", "donor", 26.1445, 91.7362, None, "medium"),
            ("Demo Receiver", "receiver.demo@example.com", "receiver", 26.1500, 91.7400, 30, "high"),
            ("Demo Volunteer", "volunteer.demo@example.com", "volunteer", 26.1550, 91.7450, None, "medium"),
        ]
        for name, email, role, lat, lon, need, priority in users:
            if db.scalar(select(User).where(User.email == email)):
                continue
            db.add(User(name=name, email=email, role=role, password_hash=hash_password("Demo-Only-Password-123!"), latitude=lat, longitude=lon, needed_quantity=need, need_priority=priority))
        db.commit()
        print("Demo users are ready. Disposable password for each: Demo-Only-Password-123!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
