from getpass import getpass
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from sqlalchemy import select  # noqa: E402
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import User  # noqa: E402


def main():
    Base.metadata.create_all(bind=engine)
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password (minimum 12 characters): ")
    if len(name) < 2 or len(password) < 12:
        raise SystemExit("Name must contain at least 2 characters and password at least 12.")
    db = SessionLocal()
    try:
        if db.scalar(select(User).where(User.email == email)):
            raise SystemExit("An account with this email already exists. Use a unique email.")
        admin = User(name=name, email=email, password_hash=hash_password(password), role="admin")
        db.add(admin)
        db.commit()
        print(f"Admin account created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
