"""Convert CSV metadata files to validated YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

from .csv_reader import read_csv
from .models import IngestionPipeline


def convert(
    metadata_dir: str | Path,
    output_dir: str | Path,
    *,
    indent: int = 2,
) -> list[Path]:
    """Read tables.csv and columns.csv, validate each pipeline, and write YAML files.

    Parameters
    ----------
    metadata_dir:
        Directory containing ``tables.csv`` and ``columns.csv``.
    output_dir:
        Directory where YAML files will be written (created if needed).
    indent:
        YAML indentation level.

    Returns
    -------
    list[Path]
        Paths of the generated YAML files.
    """
    metadata_dir = Path(metadata_dir)
    raw_pipelines = read_csv(metadata_dir / "tables.csv", metadata_dir / "columns.csv")
    if not raw_pipelines:
        raise ValueError("No pipelines found in the CSV files.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    errors: list[str] = []

    for raw in raw_pipelines:
        name = raw.get("pipeline_name", "<unknown>")
        try:
            pipeline = IngestionPipeline.model_validate(raw)
        except Exception as exc:
            errors.append(f"Pipeline '{name}': {exc}")
            continue

        out_file = output_dir / f"{pipeline.pipeline_name}.yaml"
        out_file.write_text(
            yaml.dump(pipeline.model_dump(mode="json", by_alias=True), indent=indent, sort_keys=False),
            encoding="utf-8",
        )
        written.append(out_file)

    if errors:
        msg = "Validation errors:\n" + "\n".join(errors)
        if not written:
            raise ValueError(msg)
        print(f"WARNING: {len(errors)} pipeline(s) failed validation:\n" + "\n".join(errors))

    return written
