"""create cutters table

Revision ID: 003
Revises: 002
Create Date: 2024-01-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cutters",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("model_number", sa.String(100), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        # 分类
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subcategory", sa.String(100), server_default=""),
        sa.Column("variant", sa.String(100), nullable=True),
        # 材料
        sa.Column("substrate", sa.String(50), nullable=False),
        sa.Column("coating_type", sa.String(100), nullable=True),
        sa.Column("hardness_hrc", sa.Float, nullable=True),
        sa.Column("iso_class", sa.String(20), nullable=True),
        sa.Column("material_grade", sa.String(50), nullable=True),
        # 几何
        sa.Column("diameter", sa.Float, nullable=False),
        sa.Column("length", sa.Float, nullable=False),
        sa.Column("flute_length", sa.Float, server_default="0.0"),
        sa.Column("number_of_flutes", sa.Integer, server_default="4"),
        sa.Column("helix_angle", sa.Float, server_default="30.0"),
        sa.Column("corner_radius", sa.Float, server_default="0.0"),
        # 业务数据
        sa.Column("recommended_parameters", JSONB, server_default="{}"),
        sa.Column("usage_guidelines", sa.Text, server_default=""),
        sa.Column("compatible_materials", ARRAY(sa.String), server_default="{}"),
        # 外键
        sa.Column("manufacturer_id", UUID(as_uuid=True), sa.ForeignKey("manufacturers.id"), nullable=True),
        # 时间戳
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_cutters_category", "cutters", ["category"])
    op.create_index("ix_cutters_manufacturer_id", "cutters", ["manufacturer_id"])
    op.create_index("ix_cutters_name", "cutters", ["name"])


def downgrade() -> None:
    op.drop_index("ix_cutters_name")
    op.drop_index("ix_cutters_manufacturer_id")
    op.drop_index("ix_cutters_category")
    op.drop_table("cutters")
