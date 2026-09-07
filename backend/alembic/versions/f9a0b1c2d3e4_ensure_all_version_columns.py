"""ensure all version columns for occ

Revision ID: f9a0b1c2d3e4
Revises: e8f9a0b1c2d3
Create Date: 2026-09-07 15:40:00.000000

Adds the version column to hsn_codes, units_of_measurement, master_companies,
inquiry_items, supplier_types, buyer_types, and consignment_codes to ensure
complete Optimistic Concurrency Control (OCC) alignment across all master tables.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "f9a0b1c2d3e4"
down_revision: Union[str, None] = "e8f9a0b1c2d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = [
    "hsn_codes",
    "units_of_measurement",
    "master_companies",
    "inquiry_items",
    "supplier_types",
    "buyer_types",
    "consignment_codes",
    "planning_sheets",
    "organizations",
    "positions",
    "countries",
    "states",
    "cities",
    "currencies",
    "brands",
    "product_categories",
    "product_sub_categories",
    "products",
    "suppliers",
    "buyers",
    "users",
]

def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    for table_name in TABLES:
        if insp.has_table(table_name):
            cols = {c["name"] for c in insp.get_columns(table_name)}
            if "version" not in cols:
                op.add_column(
                    table_name,
                    sa.Column("version", sa.Integer(), nullable=False, server_default="1")
                )

    if insp.has_table("planning_sheets"):
        cols = {c["name"] for c in insp.get_columns("planning_sheets")}
        if "item_description" not in cols:
            op.add_column("planning_sheets", sa.Column("item_description", sa.Text(), nullable=True))

    if insp.has_table("planning_columns"):
        cols = {c["name"] for c in insp.get_columns("planning_columns")}
        if "description" not in cols:
            op.add_column("planning_columns", sa.Column("description", sa.Text(), nullable=True))

    if insp.has_table("consignment_codes"):
        cols = {c["name"] for c in insp.get_columns("consignment_codes")}
        if "branch_id" not in cols:
            op.add_column("consignment_codes", sa.Column("branch_id", sa.String(50), nullable=True))

    if insp.has_table("inquiries"):
        cols = {c["name"] for c in insp.get_columns("inquiries")}
        if "branch_id" not in cols:
            op.add_column("inquiries", sa.Column("branch_id", sa.String(50), nullable=True))

    if insp.has_table("user_permissions"):
        cols = {c["name"] for c in insp.get_columns("user_permissions")}
        if "is_granted" not in cols:
            op.add_column("user_permissions", sa.Column("is_granted", sa.Boolean(), nullable=False, server_default="true"))


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    for table_name in [
        "hsn_codes",
        "units_of_measurement",
        "master_companies",
        "inquiry_items",
        "supplier_types",
        "buyer_types",
        "consignment_codes",
    ]:
        if insp.has_table(table_name):
            cols = {c["name"] for c in insp.get_columns(table_name)}
            if "version" in cols:
                op.drop_column(table_name, "version")
