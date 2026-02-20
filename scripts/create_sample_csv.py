"""Generate sample CSV metadata templates with two example pipelines."""

import csv
from pathlib import Path

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

TABLES_HEADERS = [
    "pipeline_name", "description",
    "source_path", "source_format", "header", "delimiter",
    "target_catalog", "target_schema", "target_table",
    "write_mode", "partition_by", "merge_keys",
]

TABLES_ROWS = [
    [
        "customers_raw", "Ingest raw customer CSV from landing zone",
        "/Volumes/main/landing/raw_data/customers.csv", "csv", "true", ",",
        "main", "bronze", "customers_raw",
        "append", "", "",
    ],
    [
        "orders_raw", "Ingest raw orders parquet",
        "/Volumes/main/landing/raw_data/orders/", "parquet", "", "",
        "main", "bronze", "orders_raw",
        "overwrite", "order_date", "",
    ],
]

COLUMNS_HEADERS = [
    "pipeline_name", "source_name", "target_name",
    "data_type", "nullable", "description", "transform",
]

COLUMNS_ROWS = [
    ["customers_raw", "customer_id", "customer_id", "long", "false", "Primary key", ""],
    ["customers_raw", "first_name", "first_name", "string", "false", "", ""],
    ["customers_raw", "last_name", "last_name", "string", "false", "", ""],
    ["customers_raw", "email", "email", "string", "true", "Contact email", ""],
    ["customers_raw", "created_at", "created_at", "timestamp", "true", "", ""],
    ["orders_raw", "order_id", "order_id", "long", "false", "PK", ""],
    ["orders_raw", "customer_id", "customer_id", "long", "false", "FK to customers", ""],
    ["orders_raw", "order_date", "order_date", "date", "false", "", ""],
    ["orders_raw", "amount", "amount_cents", "long", "true", "Amount in cents", "CAST(amount * 100 AS LONG)"],
    ["orders_raw", "status", "status", "string", "true", "", "UPPER(status)"],
]


def create_sample():
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

    tables_out = TEMPLATE_DIR / "tables.csv"
    with open(tables_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(TABLES_HEADERS)
        writer.writerows(TABLES_ROWS)
    print(f"tables.csv saved to {tables_out}")

    columns_out = TEMPLATE_DIR / "columns.csv"
    with open(columns_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS_HEADERS)
        writer.writerows(COLUMNS_ROWS)
    print(f"columns.csv saved to {columns_out}")

    return tables_out, columns_out


if __name__ == "__main__":
    create_sample()
