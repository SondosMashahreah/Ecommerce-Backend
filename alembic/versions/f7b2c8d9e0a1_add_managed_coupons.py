"""Store admin-managed coupons and preserve the existing checkout offers."""
from alembic import op
import sqlalchemy as sa

revision = "f7b2c8d9e0a1"
down_revision = "e6f8a1b2c3d4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "coupons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("discount_type", sa.String(10), nullable=False),
        sa.Column("discount_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("minimum_order", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint("discount_type IN ('percent', 'fixed')", name="ck_coupon_type"),
        sa.CheckConstraint("discount_value > 0", name="ck_coupon_positive"),
        sa.CheckConstraint("discount_type != 'percent' OR discount_value <= 100", name="ck_coupon_percent"),
        sa.CheckConstraint("minimum_order >= 0", name="ck_coupon_minimum"),
        if_not_exists=True,
    )
    op.execute("""INSERT INTO coupons (code, discount_type, discount_value, minimum_order, is_active)
                  VALUES ('SAVE10', 'percent', 10, 50, true), ('WELCOME20', 'percent', 20, 100, true)
                  ON CONFLICT (code) DO NOTHING""")


def downgrade():
    op.drop_table("coupons")
