"""Convert Excel metadata workbooks to validated JSON files."""

from __future__ import annotations

import json
from pathlib import Path

from .excel_reader import read_excel
from .models import IngestionPipeline


def convert(
    excel_path: str | Path,
    output_dir: str | Path,
    *,
    indent: int = 2,
) -> list[Path]:
    """Read an Excel workbook, validate each pipeline, and write JSON files.

    Parameters
    ----------
    excel_path:
        Path to the ``.xlsx`` workbook.
    output_dir:
        Directory where JSON files will be written (created if needed).
    indent:
        JSON indentation level.

    Returns
    -------
    list[Path]
        Paths of the generated JSON files.
    """
    raw_pipelines = read_excel(excel_path)
    if not raw_pipelines:
        raise ValueError("No pipelines found in the workbook.")

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

        out_file = output_dir / f"{pipeline.pipeline_name}.json"
        out_file.write_text(
            json.dumps(pipeline.model_dump(by_alias=True), indent=indent),
            encoding="utf-8",
        )
        written.append(out_file)

    if errors:
        msg = "Validation errors:\n" + "\n".join(errors)
        if not written:
            raise ValueError(msg)
        # Partial success — print warnings but don't crash
        print(f"WARNING: {len(errors)} pipeline(s) failed validation:\n" + "\n".join(errors))

    return written
