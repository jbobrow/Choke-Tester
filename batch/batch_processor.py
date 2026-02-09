"""
Batch processor for analysing entire folders of .stl and .3mf files.

Can be used from the CLI independently of the GUI.
"""

import csv
import json
from pathlib import Path
from typing import List, Optional, Callable, Union

import trimesh

from analyzer.choke_check import ChokeResult, fits_choke_cylinder
from analyzer.standards import ChokeStandard, US_CPSC
from integrations.read_3mf import load_3mf_objects
from reports.pdf_report import generate_report


def collect_files(folder: Union[str, Path]) -> List[Path]:
    """Return all .stl and .3mf files in *folder* (non-recursive)."""
    p = Path(folder)
    stls = sorted(p.glob("*.stl"))
    threemfs = sorted(p.glob("*.3mf"))
    return stls + threemfs


def batch_analyse(
    folder: Union[str, Path],
    standard: ChokeStandard = US_CPSC,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> List[ChokeResult]:
    """
    Analyse every .stl and .3mf file in *folder*.

    Parameters
    ----------
    folder : path
    standard : ChokeStandard
    progress_callback : callable, optional
        ``callback(current_index, total_count, filename)``

    Returns
    -------
    list of ChokeResult
    """
    files = collect_files(folder)
    results: List[ChokeResult] = []
    total = len(files)

    idx = 0
    for f in files:
        if progress_callback:
            progress_callback(idx, total, f.name)

        if f.suffix.lower() == ".stl":
            mesh = trimesh.load(str(f))
            r = fits_choke_cylinder(mesh, standard=standard, name=f.stem)
            results.append(r)
            idx += 1

        elif f.suffix.lower() == ".3mf":
            try:
                objs = load_3mf_objects(str(f))
                for o in objs:
                    r = fits_choke_cylinder(
                        o.mesh, standard=standard, name=f"{f.stem}/{o.name}"
                    )
                    results.append(r)
            except Exception as e:
                print(f"Warning: failed to load {f.name}: {e}")
            idx += 1

    if progress_callback:
        progress_callback(total, total, "Done")

    return results


def export_csv(results: List[ChokeResult], output_path: Union[str, Path]):
    """Write results to a CSV file."""
    path = Path(output_path)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Object", "Fits", "Diameter_mm", "Height_mm", "Standard"])
        for r in results:
            writer.writerow([
                r.name,
                r.fits,
                f"{r.diameter_mm:.2f}" if r.diameter_mm else "",
                f"{r.height_mm:.2f}" if r.height_mm else "",
                r.standard.name,
            ])


def export_json(results: List[ChokeResult], output_path: Union[str, Path]):
    """Write results to a JSON file."""
    path = Path(output_path)
    data = []
    for r in results:
        data.append({
            "name": r.name,
            "fits_in_cylinder": r.fits,
            "is_choking_hazard": r.fits,
            "diameter_mm": round(r.diameter_mm, 2) if r.diameter_mm else None,
            "height_mm": round(r.height_mm, 2) if r.height_mm else None,
            "standard": r.standard.name,
        })
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def batch_full_report(
    folder: Union[str, Path],
    standard: ChokeStandard = US_CPSC,
    output_dir: Optional[Union[str, Path]] = None,
) -> dict:
    """
    Run a full batch analysis and generate PDF, CSV, and JSON reports.

    Returns a dict with paths to the generated files.
    """
    folder = Path(folder)
    output_dir = Path(output_dir) if output_dir else folder

    results = batch_analyse(folder, standard)

    pdf_path = output_dir / "choke_test_report.pdf"
    csv_path = output_dir / "choke_test_results.csv"
    json_path = output_dir / "choke_test_results.json"

    generate_report(results, str(pdf_path), standard)
    export_csv(results, csv_path)
    export_json(results, json_path)

    return {
        "pdf": str(pdf_path),
        "csv": str(csv_path),
        "json": str(json_path),
        "total": len(results),
        "hazards": sum(1 for r in results if r.fits),
    }
