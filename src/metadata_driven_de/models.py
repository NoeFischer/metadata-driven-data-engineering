"""Pydantic models for ingestion pipeline metadata.

These mirror the YAML schema in schemas/ingestion_pipeline.schema.yaml and
are the single source of truth for validation at runtime.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class SourceFormat(str, Enum):
    csv = "csv"
    parquet = "parquet"
    delta = "delta"
    json = "json"
    avro = "avro"
    orc = "orc"
    xml = "xml"


class SparkDataType(str, Enum):
    string = "string"
    integer = "integer"
    long = "long"
    float = "float"
    double = "double"
    boolean = "boolean"
    date = "date"
    timestamp = "timestamp"
    decimal = "decimal"
    binary = "binary"


class WriteMode(str, Enum):
    append = "append"
    overwrite = "overwrite"
    merge = "merge"


class Source(BaseModel):
    path: str = Field(description="Volume path, e.g. /Volumes/catalog/schema/volume/path")
    format: SourceFormat
    header: bool = True
    delimiter: str = ","
    read_options: dict[str, str] = Field(default_factory=dict)


class Target(BaseModel):
    catalog: str
    schema_: str = Field(alias="schema")
    table: str
    write_mode: WriteMode = WriteMode.append
    partition_by: list[str] = Field(default_factory=list)
    merge_keys: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class Column(BaseModel):
    source_name: str
    target_name: str
    data_type: SparkDataType
    nullable: bool = True
    description: str = ""
    transform: str = ""


class IngestionPipeline(BaseModel):
    """Top-level model for a single ingestion pipeline."""

    pipeline_name: str
    description: str = ""
    source: Source
    target: Target
    columns: list[Column] = Field(min_length=1)
