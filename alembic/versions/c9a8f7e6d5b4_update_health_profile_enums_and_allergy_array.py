"""update health profile enums and allergy array

Revision ID: c9a8f7e6d5b4
Revises: b6f1d9c2e4a7
Create Date: 2026-02-25 18:20:00.000000
"""
from typing import Sequence, Union

from alembic import op


revision: str = "c9a8f7e6d5b4"
down_revision: Union[str, Sequence[str], None] = "b6f1d9c2e4a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kidney_disease_enum')
               AND NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kidneydisease_enum') THEN
                ALTER TYPE kidney_disease_enum RENAME TO kidneydisease_enum;
            END IF;
        END $$;
        """
    )

    op.execute(
        """
        CREATE TYPE allergy_enum_new AS ENUM (
            'EGG', 'MILK', 'BUCKWHEAT', 'PEANUT', 'SOYBEAN', 'WHEAT', 'MACKEREL',
            'CRAB', 'SHRIMP', 'PORK', 'PEACH', 'TOMATO', 'SULFITE', 'WALNUT',
            'CHICKEN', 'BEEF', 'SQUID', 'PINE_NUT', 'SEASAME', 'ALMOND',
            'OYSTER', 'ABALONE', 'MUSSEL'
        );
        """
    )

    op.execute(
        """
        ALTER TABLE user_health_profile
        ALTER COLUMN allergy DROP DEFAULT,
        ALTER COLUMN allergy TYPE allergy_enum_new[]
        USING (
            CASE
                WHEN allergy IS NULL OR allergy::text = 'na' THEN ARRAY[]::allergy_enum_new[]
                WHEN allergy::text = 'egg' THEN ARRAY['EGG'::allergy_enum_new]
                WHEN allergy::text = 'milk' THEN ARRAY['MILK'::allergy_enum_new]
                WHEN allergy::text = 'peanut' THEN ARRAY['PEANUT'::allergy_enum_new]
                WHEN allergy::text = 'soy' THEN ARRAY['SOYBEAN'::allergy_enum_new]
                WHEN allergy::text = 'wheat' THEN ARRAY['WHEAT'::allergy_enum_new]
                WHEN allergy::text = 'peach' THEN ARRAY['PEACH'::allergy_enum_new]
                WHEN allergy::text = 'fish' THEN ARRAY['MACKEREL'::allergy_enum_new]
                WHEN allergy::text = 'tree_nut' THEN ARRAY['WALNUT'::allergy_enum_new]
                WHEN allergy::text = 'shellfish' THEN ARRAY['SHRIMP'::allergy_enum_new]
                ELSE ARRAY[]::allergy_enum_new[]
            END
        );
        """
    )

    op.execute("DROP TYPE allergy_enum;")
    op.execute("ALTER TYPE allergy_enum_new RENAME TO allergy_enum;")
    op.execute(
        """
        ALTER TABLE user_health_profile
        ALTER COLUMN allergy SET DEFAULT '{}'::allergy_enum[],
        ALTER COLUMN allergy SET NOT NULL;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE TYPE allergy_enum_old AS ENUM (
            'egg', 'milk', 'peanut', 'tree_nut', 'shellfish', 'fish', 'wheat', 'soy', 'peach', 'na'
        );
        """
    )
    op.execute(
        """
        ALTER TABLE user_health_profile
        ALTER COLUMN allergy DROP DEFAULT,
        ALTER COLUMN allergy DROP NOT NULL,
        ALTER COLUMN allergy TYPE allergy_enum_old
        USING (
            CASE
                WHEN allergy IS NULL OR cardinality(allergy) = 0 THEN 'na'::allergy_enum_old
                WHEN allergy[1]::text = 'EGG' THEN 'egg'::allergy_enum_old
                WHEN allergy[1]::text = 'MILK' THEN 'milk'::allergy_enum_old
                WHEN allergy[1]::text = 'PEANUT' THEN 'peanut'::allergy_enum_old
                WHEN allergy[1]::text = 'SOYBEAN' THEN 'soy'::allergy_enum_old
                WHEN allergy[1]::text = 'WHEAT' THEN 'wheat'::allergy_enum_old
                WHEN allergy[1]::text = 'PEACH' THEN 'peach'::allergy_enum_old
                WHEN allergy[1]::text = 'MACKEREL' THEN 'fish'::allergy_enum_old
                WHEN allergy[1]::text = 'WALNUT' THEN 'tree_nut'::allergy_enum_old
                WHEN allergy[1]::text IN ('CRAB', 'SHRIMP', 'OYSTER', 'ABALONE', 'MUSSEL') THEN 'shellfish'::allergy_enum_old
                ELSE 'na'::allergy_enum_old
            END
        );
        """
    )
    op.execute("DROP TYPE allergy_enum;")
    op.execute("ALTER TYPE allergy_enum_old RENAME TO allergy_enum;")

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kidneydisease_enum')
               AND NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kidney_disease_enum') THEN
                ALTER TYPE kidneydisease_enum RENAME TO kidney_disease_enum;
            END IF;
        END $$;
        """
    )
