"""End-to-end tests: Excel -> YAML -> validate."""

from pathlib import Path

import yaml
import pytest

from metadata_driven_de.converter import convert
from metadata_driven_de.models import IngestionPipeline

SAMPLE_XLSX = Path(__file__).resolve().parent.parent / "templates" / "sample_metadata.xlsx"


@pytest.fixture
def output_dir(tmp_path):
    return tmp_path / "yaml_output"


@pytest.mark.skipif(not SAMPLE_XLSX.exists(), reason="sample xlsx not generated")
def test_convert_produces_yaml_files(output_dir):
    files = convert(SAMPLE_XLSX, output_dir)
    assert len(files) == 2
    names = {f.stem for f in files}
    assert names == {"customers_raw", "orders_raw"}


@pytest.mark.skipif(not SAMPLE_XLSX.exists(), reason="sample xlsx not generated")
def test_generated_yaml_is_valid(output_dir):
    files = convert(SAMPLE_XLSX, output_dir)
    for fp in files:
        data = yaml.safe_load(fp.read_text())
        pipeline = IngestionPipeline.model_validate(data)
        assert pipeline.pipeline_name == fp.stem


@pytest.mark.skipif(not SAMPLE_XLSX.exists(), reason="sample xlsx not generated")
def test_customers_pipeline_content(output_dir):
    convert(SAMPLE_XLSX, output_dir)
    data = yaml.safe_load((output_dir / "customers_raw.yaml").read_text())
    assert data["source"]["format"] == "csv"
    assert data["target"]["catalog"] == "main"
    assert len(data["columns"]) == 5
    assert data["columns"][0]["source_name"] == "customer_id"


@pytest.mark.skipif(not SAMPLE_XLSX.exists(), reason="sample xlsx not generated")
def test_orders_pipeline_has_transform(output_dir):
    convert(SAMPLE_XLSX, output_dir)
    data = yaml.safe_load((output_dir / "orders_raw.yaml").read_text())
    amount_col = next(c for c in data["columns"] if c["target_name"] == "amount_cents")
    assert "CAST" in amount_col["transform"]
    assert data["target"]["partition_by"] == ["order_date"]
