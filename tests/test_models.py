"""Tests for Pydantic models."""

import pytest
from metadata_driven_de.models import IngestionPipeline


VALID_PIPELINE = {
    "pipeline_name": "test_pipeline",
    "description": "A test pipeline",
    "source": {
        "path": "/Volumes/cat/sch/vol/file.csv",
        "format": "csv",
    },
    "target": {
        "catalog": "cat",
        "schema": "sch",
        "table": "tbl",
    },
    "columns": [
        {
            "source_name": "id",
            "target_name": "id",
            "data_type": "long",
        }
    ],
}


def test_valid_pipeline():
    p = IngestionPipeline.model_validate(VALID_PIPELINE)
    assert p.pipeline_name == "test_pipeline"
    assert p.source.format.value == "csv"
    assert p.target.schema_ == "sch"
    assert len(p.columns) == 1


def test_defaults_applied():
    p = IngestionPipeline.model_validate(VALID_PIPELINE)
    assert p.source.header is True
    assert p.source.delimiter == ","
    assert p.target.write_mode.value == "append"
    assert p.columns[0].nullable is True


def test_missing_columns_fails():
    data = {**VALID_PIPELINE, "columns": []}
    with pytest.raises(Exception):
        IngestionPipeline.model_validate(data)


def test_invalid_format_fails():
    data = {
        **VALID_PIPELINE,
        "source": {**VALID_PIPELINE["source"], "format": "excel"},
    }
    with pytest.raises(Exception):
        IngestionPipeline.model_validate(data)


def test_roundtrip_json():
    p = IngestionPipeline.model_validate(VALID_PIPELINE)
    dumped = p.model_dump(by_alias=True)
    p2 = IngestionPipeline.model_validate(dumped)
    assert p2.pipeline_name == p.pipeline_name
    assert dumped["target"]["schema"] == "sch"
