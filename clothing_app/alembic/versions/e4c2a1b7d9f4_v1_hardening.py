"""V1 backend hardening: tenancy, reservations, idempotency, and invariants."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "e4c2a1b7d9f4"
down_revision: Union[str, Sequence[str], None] = "bc565804fbc9"
branch_labels = None
depends_on = None
SCHEMA = "clothing_store"


def upgrade() -> None:
    """Apply V1 structural hardening without changing existing route contracts."""
    op.create_table(
        "stores",
        sa.Column("store_id", sa.String(length=50), nullable=False),
        sa.Column("store_name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("store_id", name="pk_stores"),
        schema=SCHEMA,
    )
    op.execute("INSERT INTO clothing_store.stores(store_id, store_name, is_active) VALUES ('northstar', 'Northstar Menswear', TRUE) ON CONFLICT (store_id) DO NOTHING")

    # Store-scope existing catalog rows before enforcing not-null FKs.
    for table in ("branches", "categories", "products", "product_variants", "offers"):
        op.add_column(table, sa.Column("store_id", sa.String(length=50), nullable=True), schema=SCHEMA)
        op.execute(f"UPDATE {SCHEMA}.{table} SET store_id = 'northstar' WHERE store_id IS NULL")
        op.alter_column(table, "store_id", nullable=False, schema=SCHEMA)
        op.create_foreign_key(
            f"fk_{table}_store_id_stores",
            table,
            "stores",
            ["store_id"],
            ["store_id"],
            source_schema=SCHEMA,
            referent_schema=SCHEMA,
            ondelete="CASCADE",
        )

    for table, old_name, cols, new_name in [
        ("branches", "uq_branches_branch_code", ["store_id", "branch_code"], "uq_branches_store_code"),
        ("categories", "uq_categories_category_code", ["store_id", "category_code"], "uq_categories_store_code"),
        ("products", "uq_products_article_code", ["store_id", "article_code"], "uq_products_store_article"),
        ("product_variants", "uq_product_variants_sku", ["store_id", "sku"], "uq_variants_store_sku"),
    ]:
        try:
            op.drop_constraint(old_name, table_name=table, schema=SCHEMA, type_="unique")
        except Exception:
            pass
        op.create_unique_constraint(new_name, table, cols, schema=SCHEMA)

    op.add_column("orders", sa.Column("checkout_request_id", sa.String(length=100), nullable=True), schema=SCHEMA)
    op.create_unique_constraint("uq_orders_checkout_request_id", "orders", ["checkout_request_id"], schema=SCHEMA)
    op.create_foreign_key("fk_carts_store_id_stores", "carts", "stores", ["store_id"], ["store_id"], source_schema=SCHEMA, referent_schema=SCHEMA, ondelete="CASCADE")
    op.create_foreign_key("fk_orders_store_id_stores", "orders", "stores", ["store_id"], ["store_id"], source_schema=SCHEMA, referent_schema=SCHEMA, ondelete="CASCADE")

    op.create_table(
        "inventory_reservations",
        sa.Column("reservation_id", sa.Uuid(), nullable=False),
        sa.Column("cart_id", sa.Uuid(), nullable=False),
        sa.Column("variant_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.ForeignKeyConstraint(["cart_id"], [f"{SCHEMA}.carts.cart_id"], ondelete="CASCADE", name="fk_inventory_reservations_cart"),
        sa.PrimaryKeyConstraint("reservation_id", name="pk_inventory_reservations"),
        sa.UniqueConstraint("cart_id", "variant_id", "branch_id", name="uq_inventory_reservation_cart_variant_branch"),
        schema=SCHEMA,
    )

    op.create_check_constraint("ck_cart_items_positive_quantity", "cart_items", "quantity > 0", schema=SCHEMA)
    op.create_check_constraint("ck_inventory_quantity_on_hand_non_negative", "branch_inventory", "quantity_on_hand >= 0", schema=SCHEMA)
    op.create_check_constraint("ck_inventory_reserved_non_negative", "branch_inventory", "reserved_quantity >= 0", schema=SCHEMA)
    op.create_check_constraint("ck_inventory_damaged_non_negative", "branch_inventory", "damaged_quantity >= 0", schema=SCHEMA)
    op.create_check_constraint("ck_inventory_in_transit_non_negative", "branch_inventory", "in_transit_quantity >= 0", schema=SCHEMA)
    op.create_check_constraint("ck_inventory_available_consistent", "branch_inventory", "quantity_on_hand >= reserved_quantity + damaged_quantity", schema=SCHEMA)
    op.create_check_constraint("ck_offers_discount_percentage_non_negative", "offers", "discount_percentage IS NULL OR discount_percentage >= 0", schema=SCHEMA)
    op.create_check_constraint("ck_offers_discount_amount_non_negative", "offers", "discount_amount IS NULL OR discount_amount >= 0", schema=SCHEMA)
    op.create_check_constraint("ck_offers_min_cart_value_non_negative", "offers", "min_cart_value IS NULL OR min_cart_value >= 0", schema=SCHEMA)
    op.create_check_constraint("ck_offers_min_quantity_positive", "offers", "min_quantity IS NULL OR min_quantity > 0", schema=SCHEMA)
    op.create_check_constraint("ck_offers_valid_window", "offers", "valid_until IS NULL OR valid_until > valid_from", schema=SCHEMA)


def downgrade() -> None:
    """Reverse the hardening migration."""
    for name, table in [
        ("ck_offers_valid_window", "offers"),
        ("ck_offers_min_quantity_positive", "offers"),
        ("ck_offers_min_cart_value_non_negative", "offers"),
        ("ck_offers_discount_amount_non_negative", "offers"),
        ("ck_offers_discount_percentage_non_negative", "offers"),
        ("ck_inventory_available_consistent", "branch_inventory"),
        ("ck_inventory_in_transit_non_negative", "branch_inventory"),
        ("ck_inventory_damaged_non_negative", "branch_inventory"),
        ("ck_inventory_reserved_non_negative", "branch_inventory"),
        ("ck_inventory_quantity_on_hand_non_negative", "branch_inventory"),
        ("ck_cart_items_positive_quantity", "cart_items"),
    ]:
        op.drop_constraint(name, table_name=table, schema=SCHEMA, type_="check")
    op.drop_table("inventory_reservations", schema=SCHEMA)
    op.drop_constraint("fk_orders_store_id_stores", table_name="orders", schema=SCHEMA, type_="foreignkey")
    op.drop_constraint("fk_carts_store_id_stores", table_name="carts", schema=SCHEMA, type_="foreignkey")
    op.drop_constraint("uq_orders_checkout_request_id", table_name="orders", schema=SCHEMA, type_="unique")
    op.drop_column("orders", "checkout_request_id", schema=SCHEMA)

    for table, old_name, new_name in [
        ("branches", "uq_branches_branch_code", "uq_branches_store_code"),
        ("categories", "uq_categories_category_code", "uq_categories_store_code"),
        ("products", "uq_products_article_code", "uq_products_store_article"),
        ("product_variants", "uq_product_variants_sku", "uq_variants_store_sku"),
    ]:
        op.drop_constraint(new_name, table_name=table, schema=SCHEMA, type_="unique")
        op.create_unique_constraint(old_name, table, ["branch_code" if table == "branches" else "category_code" if table == "categories" else "article_code" if table == "products" else "sku"], schema=SCHEMA)

    for table in ("offers", "product_variants", "products", "categories", "branches"):
        op.drop_constraint(f"fk_{table}_store_id_stores", table_name=table, schema=SCHEMA, type_="foreignkey")
        op.drop_column(table, "store_id", schema=SCHEMA)
    op.drop_table("stores", schema=SCHEMA)
