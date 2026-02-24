"""add cart_items

Revision ID: 792bb0e54847
Revises: 5d17c68389df
Create Date: 2026-02-23 05:28:43.361249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "792bb0e54847"
down_revision: Union[str, Sequence[str], None] = "5d17c68389df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    ✅ 목표: cart_items 테이블 생성 + products numeric->float 타입 변경 적용
    ❌ 제외: products.brand UNIQUE(uq_products_brand) 추가
       - 현재 DB에 brand 중복(예: 남원혼불부각)이 있어 UNIQUE 생성이 실패함
       - UNIQUE는 데이터 정리 후 별도 migration으로 처리하는 게 안전
    """

    # --- 1) cart_items 생성 ---
    op.create_table(
        "cart_items",
        sa.Column("item_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column(
            "analysis_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("item_id"),
    )
    op.create_index(op.f("ix_cart_items_product_id"), "cart_items", ["product_id"], unique=False)
    op.create_index(op.f("ix_cart_items_user_id"), "cart_items", ["user_id"], unique=False)

    # --- 2) products 컬럼 타입 변경 (NUMERIC -> Float) ---
    op.alter_column("products", "kcal", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "protein_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "fat_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "ash_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "carb_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "sugar_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "sodium_mg", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "cholesterol_mg", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "sat_fat_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "trans_fat_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "nutrient_basis_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "serving_ref_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "food_weight_g", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "gi", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)
    op.alter_column("products", "gl", existing_type=sa.NUMERIC(), type_=sa.Float(), existing_nullable=True)

    # ❌ 여기 있었던 UNIQUE 제거 (중복 때문에 upgrade 실패)
    # op.create_unique_constraint("uq_products_brand", "products", ["brand"])


def downgrade() -> None:
    """Downgrade schema.

    upgrade에서 brand UNIQUE는 안 했으니 downgrade에서도 제거/복구하지 않음.
    """

    # --- 1) products 타입 되돌리기 (Float -> NUMERIC) ---
    op.alter_column("products", "gl", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "gi", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "food_weight_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "serving_ref_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "nutrient_basis_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "trans_fat_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "sat_fat_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "cholesterol_mg", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "sodium_mg", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "sugar_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "carb_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "ash_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "fat_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "protein_g", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)
    op.alter_column("products", "kcal", existing_type=sa.Float(), type_=sa.NUMERIC(), existing_nullable=True)

    # --- 2) cart_items 제거 ---
    op.drop_index(op.f("ix_cart_items_user_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_product_id"), table_name="cart_items")
    op.drop_table("cart_items")