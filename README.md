# metadata-driven-data-engineering

A lightweight framework for defining PySpark / Databricks ingestion pipelines as metadata. You describe your pipelines in two CSV files; the tool validates them and emits one YAML config file per pipeline.

## How it works

```
templates/
  tables.csv    ← one row per pipeline (source, target, write mode …)
  columns.csv   ← one row per column (name, type, optional transform …)
        │
        ▼  mdde convert
output/
  customers_raw.yaml
  orders_raw.yaml
  …
```

## Installation

Requires Python 3.10+. Install with [uv](https://github.com/astral-sh/uv) (recommended) or pip:

```bash
uv venv .venv
uv pip install -e ".[dev]"
```

## Usage

### Convert CSV metadata to YAML

```bash
mdde convert path/to/metadata/ -o output/
```

The `metadata/` directory must contain `tables.csv` and `columns.csv`.

### Validate existing YAML files

```bash
mdde validate output/customers_raw.yaml output/orders_raw.yaml
```

## CSV format

### tables.csv

| Column | Required | Description |
|---|---|---|
| `pipeline_name` | yes | Unique pipeline identifier |
| `description` | | Human-readable description |
| `source_path` | yes | Path to the source data (e.g. Unity Catalog volume path) |
| `source_format` | yes | `csv`, `parquet`, `delta`, `json`, `avro`, `orc`, `xml` |
| `header` | | `true`/`false` — whether source has a header row (default: `true`) |
| `delimiter` | | CSV delimiter (default: `,`) |
| `target_catalog` | yes | Unity Catalog catalog name |
| `target_schema` | yes | Unity Catalog schema name |
| `target_table` | yes | Target table name |
| `write_mode` | | `append`, `overwrite`, or `merge` (default: `append`) |
| `partition_by` | | Comma-separated list of partition columns |
| `merge_keys` | | Comma-separated list of merge key columns |
| `opt_*` | | Any column prefixed `opt_` is passed as a Spark read option |

### columns.csv

| Column | Required | Description |
|---|---|---|
| `pipeline_name` | yes | Must match a row in `tables.csv` |
| `source_name` | yes | Column name in the source data |
| `target_name` | yes | Column name in the target table |
| `data_type` | yes | Spark SQL type: `string`, `integer`, `long`, `float`, `double`, `boolean`, `date`, `timestamp`, `decimal`, `binary` |
| `nullable` | | `true`/`false` (default: `true`) |
| `description` | | Column description |
| `transform` | | Optional Spark SQL expression, e.g. `UPPER(status)` |

See `templates/` for working examples.

## Output

Each pipeline produces a validated YAML file:

```yaml
pipeline_name: customers_raw
description: Ingest raw customer CSV from landing zone
source:
  path: /Volumes/main/landing/raw_data/customers.csv
  format: csv
  header: true
  delimiter: ','
  read_options: {}
target:
  catalog: main
  schema: bronze
  table: customers_raw
  write_mode: append
  partition_by: []
  merge_keys: []
columns:
  - source_name: customer_id
    target_name: customer_id
    data_type: long
    nullable: false
    description: Primary key
    transform: ''
```

## Development

```bash
# run tests
.venv/bin/pytest tests/ -v

# regenerate sample CSV templates
.venv/bin/python scripts/create_sample_csv.py
```
