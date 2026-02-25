"""drop unique constraint on products.brand

Revision ID: b6f1d9c2e4a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-25 12:25:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b6f1d9c2e4a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'uq_products_brand'
            ) THEN
                ALTER TABLE public.products DROP CONSTRAINT uq_products_brand;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'uq_products_brand'
            ) THEN
                ALTER TABLE public.products
                ADD CONSTRAINT uq_products_brand UNIQUE (brand);
            END IF;
        END $$;
        """
    )
