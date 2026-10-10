"""Create new ShareBite tables and upgrade the previous SQLite schema.

Revision ID: 20261010_0001
Revises:
Create Date: 2026-10-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from app.core.database import Base
import app.models  # noqa: F401

revision = "20261010_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    # An empty database is bootstrapped from the current model metadata.
    if "users" not in tables:
        Base.metadata.create_all(bind=bind)
        return

    # Bring the older bundled schema forward without dropping existing accounts or donations.
    columns = {c["name"] for c in inspector.get_columns("users")}
    if "needed_quantity" not in columns:
        op.add_column("users", sa.Column("needed_quantity", sa.Float(), nullable=True))
    if "need_priority" not in columns:
        op.add_column("users", sa.Column("need_priority", sa.String(length=20), nullable=False, server_default="medium"))

    inspector = inspect(bind)
    if "donations" in inspector.get_table_names():
        columns = {c["name"] for c in inspector.get_columns("donations")}
        if "photo_url" not in columns:
            op.add_column("donations", sa.Column("photo_url", sa.String(length=2048), nullable=True))
        if "pickup_address" not in columns:
            op.add_column("donations", sa.Column("pickup_address", sa.String(length=500), nullable=True))

    # Also create deliveries and notifications if they do not yet exist.
    Base.metadata.create_all(bind=bind)


def downgrade():
    # Data-preserving downgrade is intentionally omitted; dropping tables/columns can destroy user data.
    raise RuntimeError("This migration is data-preserving and has no automatic downgrade. Restore a database backup to roll back.")
