"""alter kidney_disease_enum to CKD_3_5, HD, PD, na

Revision ID: a1b2c3d4e5f6
Revises: 792bb0e54847
Create Date: 2026-02-24

kidney_disease_enum: (chronic_kidney_disease, kidney_failure, ...) -> (CKD_3_5, HD, PD, na)
기존 데이터 매핑: kidney_failure->HD, na->na, 그 외->CKD_3_5
"""
from typing import Sequence, Union

from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "792bb0e54847"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TYPE kidney_disease_enum_new AS ENUM ('CKD_3_5', 'HD', 'PD', 'na')
    """)
    op.execute("""
        ALTER TABLE user_health_profile
        ALTER COLUMN kidneydisease TYPE kidney_disease_enum_new
        USING (
            CASE kidneydisease::text
                WHEN 'kidney_failure' THEN 'HD'::kidney_disease_enum_new
                WHEN 'na' THEN 'na'::kidney_disease_enum_new
                ELSE 'CKD_3_5'::kidney_disease_enum_new
            END
        )
    """)
    op.execute("DROP TYPE kidney_disease_enum")
    op.execute("ALTER TYPE kidney_disease_enum_new RENAME TO kidney_disease_enum")


def downgrade() -> None:
    op.execute("""
        CREATE TYPE kidney_disease_enum_old AS ENUM (
            'chronic_kidney_disease', 'kidney_failure', 'kidney_stones',
            'proteinuria', 'nephrotic_syndrome', 'na'
        )
    """)
    op.execute("""
        ALTER TABLE user_health_profile
        ALTER COLUMN kidneydisease TYPE kidney_disease_enum_old
        USING (
            CASE kidneydisease::text
                WHEN 'HD' THEN 'kidney_failure'::kidney_disease_enum_old
                WHEN 'na' THEN 'na'::kidney_disease_enum_old
                ELSE 'chronic_kidney_disease'::kidney_disease_enum_old
            END
        )
    """)
    op.execute("DROP TYPE kidney_disease_enum")
    op.execute("ALTER TYPE kidney_disease_enum_old RENAME TO kidney_disease_enum")
