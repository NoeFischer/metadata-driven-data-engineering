"""Read pipeline metadata from CSV files.

Expected layout
---------------
Two CSV files in the same directory:

**tables.csv**
    Each row is one pipeline / table. Columns:
    pipeline_name, description, source_path, source_format, header, delimiter,
    target_catalog, target_schema, target_table, write_mode, partition_by, merge_keys

**columns.csv**
    Each row is one column mapping. Columns:
    pipeline_name, source_name, target_name, data_type, nullable, description, transform

The two files are joined on ``pipeline_name``.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def _parse_list_field(value: Any) -> list[str]:
    """Turn a comma-separated cell value into a list of strings."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return []
    return [v.strip() for v in str(value).split(",") if v.strip()]


def _parse_bool(value: Any, default: bool = True) -> bool:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes")


def _read_csv_file(path: Path) -> list[dict[str, str]]:
    """Read a CSV file and return a list of row dicts (header row as keys)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            {k.strip().lower(): (v.strip() if v is not None else "") for k, v in row.items() if k is not None}
            for row in reader
            if any(v and v.strip() for v in row.values())
        ]


def _build_read_options(row: dict[str, str]) -> dict[str, str]:
    """Extract any column starting with ``opt_`` as a Spark read option."""
    prefix = "opt_"
    return {
        k[len(prefix):]: v
        for k, v in row.items()
        if k.startswith(prefix) and v
    }


def read_csv(tables_path: str | Path, columns_path: str | Path) -> list[dict[str, Any]]:
    """Parse tables.csv and columns.csv into a list of raw pipeline dicts.

    Returns a list of dicts ready to be passed into
    ``IngestionPipeline.model_validate()``.
    """
    tables_path = Path(tables_path)
    columns_path = Path(columns_path)

    if not tables_path.exists():
        raise FileNotFoundError(f"tables CSV not found: {tables_path}")
    if not columns_path.exists():
        raise FileNotFoundError(f"columns CSV not found: {columns_path}")

    table_rows = _read_csv_file(tables_path)
    column_rows = _read_csv_file(columns_path)

    # Group columns by pipeline_name
    cols_by_pipeline: dict[str, list[dict]] = {}
    for cr in column_rows:
        pname = cr.get("pipeline_name", "").strip()
        if not pname:
            continue
        cols_by_pipeline.setdefault(pname, []).append(
            {
                "source_name": cr.get("source_name", ""),
                "target_name": cr.get("target_name", ""),
                "data_type": cr.get("data_type", "string").strip().lower() or "string",
                "nullable": _parse_bool(cr.get("nullable"), default=True),
                "description": cr.get("description", ""),
                "transform": cr.get("transform", ""),
            }
        )

    pipelines: list[dict[str, Any]] = []
    for row in table_rows:
        pname = row.get("pipeline_name", "").strip()
        if not pname:
            continue

        pipeline = {
            "pipeline_name": pname,
            "description": row.get("description", ""),
            "source": {
                "path": row.get("source_path", ""),
                "format": row.get("source_format", "csv").strip().lower() or "csv",
                "header": _parse_bool(row.get("header"), default=True),
                "delimiter": row.get("delimiter") or ",",
                "read_options": _build_read_options(row),
            },
            "target": {
                "catalog": row.get("target_catalog", ""),
                "schema": row.get("target_schema", ""),
                "table": row.get("target_table", ""),
                "write_mode": row.get("write_mode") or "append",
                "partition_by": _parse_list_field(row.get("partition_by")),
                "merge_keys": _parse_list_field(row.get("merge_keys")),
            },
            "columns": cols_by_pipeline.get(pname, []),
        }
        pipelines.append(pipeline)

    return pipelines
