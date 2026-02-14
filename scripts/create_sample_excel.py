"""Generate a sample Excel metadata template with two example pipelines."""

from openpyxl import Workbook
from pathlib import Path

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def create_sample():
    wb = Workbook()

    # --- tables sheet ---
    ws_tables = wb.active
    ws_tables.title = "tables"
    ws_tables.append([
        "pipeline_name", "description",
        "source_path", "source_format", "header", "delimiter",
        "target_catalog", "target_schema", "target_table",
        "write_mode", "partition_by", "merge_keys",
    ])
    ws_tables.append([
        "customers_raw", "Ingest raw customer CSV from landing zone",
        "/Volumes/main/landing/raw_data/customers.csv", "csv", True, ",",
        "main", "bronze", "customers_raw",
        "append", "", "",
    ])
    ws_tables.append([
        "orders_raw", "Ingest raw orders parquet",
        "/Volumes/main/landing/raw_data/orders/", "parquet", None, None,
        "main", "bronze", "orders_raw",
        "overwrite", "order_date", "",
    ])

    # --- columns sheet ---
    ws_cols = wb.create_sheet("columns")
    ws_cols.append([
        "pipeline_name", "source_name", "target_name",
        "data_type", "nullable", "description", "transform",
    ])
    # customers columns
    for src, tgt, dtype, nullable, desc, transform in [
        ("customer_id", "customer_id", "long", False, "Primary key", ""),
        ("first_name", "first_name", "string", False, "", ""),
        ("last_name", "last_name", "string", False, "", ""),
        ("email", "email", "string", True, "Contact email", ""),
        ("created_at", "created_at", "timestamp", True, "", ""),
    ]:
        ws_cols.append(["customers_raw", src, tgt, dtype, nullable, desc, transform])

    # orders columns
    for src, tgt, dtype, nullable, desc, transform in [
        ("order_id", "order_id", "long", False, "PK", ""),
        ("customer_id", "customer_id", "long", False, "FK to customers", ""),
        ("order_date", "order_date", "date", False, "", ""),
        ("amount", "amount_cents", "long", True, "Amount in cents", "CAST(amount * 100 AS LONG)"),
        ("status", "status", "string", True, "", "UPPER(status)"),
    ]:
        ws_cols.append(["orders_raw", src, tgt, dtype, nullable, desc, transform])

    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    out = TEMPLATE_DIR / "sample_metadata.xlsx"
    wb.save(out)
    print(f"Sample workbook saved to {out}")
    return out


if __name__ == "__main__":
    create_sample()
