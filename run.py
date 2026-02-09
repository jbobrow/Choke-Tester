#!/usr/bin/env python3
"""
Choke Test Safety Check — entry point.

Usage:
    python run.py                        # Launch GUI
    python run.py --file my_project.3mf  # Open file directly in GUI
    python run.py --batch /path/to/folder # CLI batch mode
    python run.py --cli  model.stl       # CLI single-file mode

See --help for all options.
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Choke Test Safety Check for 3D-printed objects"
    )
    parser.add_argument(
        "--file", "-f",
        help="Open a .3mf or .stl file directly in the GUI",
    )
    parser.add_argument(
        "--batch", "-b",
        help="Batch-process a folder (CLI, no GUI). Generates PDF/CSV/JSON.",
    )
    parser.add_argument(
        "--cli", "-c",
        help="Analyse a single file from the CLI (no GUI).",
    )
    parser.add_argument(
        "--standard", "-s",
        default="us_cpsc",
        choices=["us_cpsc", "eu_en71"],
        help="Which safety standard to use (default: us_cpsc)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory for batch reports (defaults to the input folder).",
    )

    args = parser.parse_args()

    # ── CLI: batch mode ──────────────────────────────────────────────────
    if args.batch:
        from analyzer.standards import get_standard
        from batch.batch_processor import batch_full_report

        std = get_standard(args.standard)
        output_dir = args.output or args.batch

        print(f"Batch analysing: {args.batch}")
        print(f"Standard: {std.name} ({std.diameter_mm}mm x {std.height_mm}mm)")
        print()

        report = batch_full_report(args.batch, std, output_dir)

        print(f"Results: {report['total']} objects, {report['hazards']} hazards")
        print(f"  PDF:  {report['pdf']}")
        print(f"  CSV:  {report['csv']}")
        print(f"  JSON: {report['json']}")
        return

    # ── CLI: single file mode ────────────────────────────────────────────
    if args.cli:
        from analyzer.standards import get_standard
        from analyzer.choke_check import fits_choke_cylinder
        import trimesh

        std = get_standard(args.standard)
        path = Path(args.cli)

        print(f"Analysing: {path.name}")
        print(f"Standard: {std.name}")
        print()

        if path.suffix.lower() == ".3mf":
            from integrations.read_3mf import load_3mf_objects
            objs = load_3mf_objects(str(path))
            for o in objs:
                result = fits_choke_cylinder(o.mesh, standard=std, name=o.name)
                _print_result(result)
        else:
            mesh = trimesh.load(str(path))
            result = fits_choke_cylinder(mesh, standard=std, name=path.stem)
            _print_result(result)
        return

    # ── GUI mode ─────────────────────────────────────────────────────────
    from ui.app import run_app
    run_app(open_path=args.file)


def _print_result(result):
    status = "\u26a0  CHOKING HAZARD" if result.fits else "\u2714  SAFE"
    print(f"  {result.name}: {status}")
    if result.diameter_mm is not None:
        print(f"    Min enclosing circle: \u00d8{result.diameter_mm:.1f} mm")
        print(f"    Height at best orientation: {result.height_mm:.1f} mm")
    print()


if __name__ == "__main__":
    main()
