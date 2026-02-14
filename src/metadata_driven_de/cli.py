"""CLI entry point: ``mdde convert``."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mdde",
        description="Metadata-driven data engineering CLI",
    )
    sub = parser.add_subparsers(dest="command")

    # --- convert ---
    p_conv = sub.add_parser("convert", help="Convert Excel metadata to JSON")
    p_conv.add_argument("excel", help="Path to the .xlsx workbook")
    p_conv.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Directory for generated JSON files (default: output/)",
    )
    p_conv.add_argument(
        "--indent", type=int, default=2, help="JSON indent (default: 2)"
    )

    # --- validate ---
    p_val = sub.add_parser("validate", help="Validate existing JSON metadata files")
    p_val.add_argument("json_files", nargs="+", help="JSON file(s) to validate")

    args = parser.parse_args(argv)

    if args.command == "convert":
        from .converter import convert

        written = convert(args.excel, args.output_dir, indent=args.indent)
        for p in written:
            print(f"  wrote {p}")
        print(f"Done — {len(written)} file(s) generated.")

    elif args.command == "validate":
        import json
        from .models import IngestionPipeline

        ok = 0
        for fp in args.json_files:
            try:
                with open(fp) as f:
                    data = json.load(f)
                IngestionPipeline.model_validate(data)
                print(f"  OK    {fp}")
                ok += 1
            except Exception as exc:
                print(f"  FAIL  {fp}: {exc}")
        print(f"Validated {ok}/{len(args.json_files)} file(s).")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
