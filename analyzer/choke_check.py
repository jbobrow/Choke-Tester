"""
Core choke-test analysis engine.

Features:
  - Two-phase rotation search (coarse → fine) for performance
  - Configurable safety standards
  - Result caching via mesh hash
  - Progress callback for UI integration
"""

import hashlib
import trimesh
import numpy as np
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Tuple

from .rotations import (
    sample_rotations,
    refine_rotations,
    rotation_to_euler,
    count_rotations,
)
from .enclosing_circle import minimal_enclosing_circle
from .standards import ChokeStandard, US_CPSC


@dataclass
class ChokeResult:
    """Outcome of a choke-test analysis for one object."""
    name: str
    fits: bool
    diameter_mm: Optional[float]
    height_mm: Optional[float]
    rotation: Optional[np.ndarray]
    standard: ChokeStandard

    @property
    def status_text(self) -> str:
        if self.fits:
            return f"FAIL — fits inside {self.standard.name} cylinder"
        return f"PASS — exceeds {self.standard.name} cylinder"


# ── Result cache ─────────────────────────────────────────────────────────────

_cache: Dict[str, ChokeResult] = {}


def _mesh_hash(mesh: trimesh.Trimesh, standard: ChokeStandard) -> str:
    """Deterministic hash for a mesh + standard combination."""
    h = hashlib.sha256()
    h.update(mesh.vertices.tobytes())
    h.update(mesh.faces.tobytes())
    h.update(standard.name.encode())
    h.update(str(standard.diameter_mm).encode())
    h.update(str(standard.height_mm).encode())
    return h.hexdigest()


def clear_cache() -> None:
    _cache.clear()


# ── Main analysis function ───────────────────────────────────────────────────

def fits_choke_cylinder(
    mesh: trimesh.Trimesh,
    standard: ChokeStandard = US_CPSC,
    coarse_step_deg: float = 15,
    fine_step_deg: float = 3,
    name: str = "Object",
    progress_callback: Optional[Callable[[float, str], None]] = None,
    use_cache: bool = True,
) -> ChokeResult:
    """
    Determine whether *mesh* fits inside the choke-test cylinder defined
    by *standard*.

    Parameters
    ----------
    mesh : trimesh.Trimesh
        The mesh to test.
    standard : ChokeStandard
        Cylinder dimensions to test against.
    coarse_step_deg : float
        Rotation increment for the first (coarse) sweep.
    fine_step_deg : float
        Rotation increment for the second (refinement) sweep.
    name : str
        Human-readable name for this object (used in results / reports).
    progress_callback : callable, optional
        ``callback(fraction, message)`` called periodically so the UI
        can show progress.  *fraction* is in [0, 1].
    use_cache : bool
        If True, return cached results when the mesh has not changed.

    Returns
    -------
    ChokeResult
    """
    # ── Cache lookup ─────────────────────────────────────────────────────
    if use_cache:
        key = _mesh_hash(mesh, standard)
        if key in _cache:
            cached = _cache[key]
            # Update name (same mesh may have different label)
            return ChokeResult(
                name=name,
                fits=cached.fits,
                diameter_mm=cached.diameter_mm,
                height_mm=cached.height_mm,
                rotation=cached.rotation,
                standard=cached.standard,
            )

    # ── Prepare mesh ─────────────────────────────────────────────────────
    clean = mesh.copy()
    # Remove degenerate faces (zero-area)
    mask = clean.nondegenerate_faces()
    if mask is not None and not mask.all():
        clean.update_faces(mask)
    clean.remove_unreferenced_vertices()
    hull = clean.convex_hull

    cyl_diameter = standard.diameter_mm
    cyl_height = standard.height_mm

    def _report(frac: float, msg: str) -> None:
        if progress_callback:
            progress_callback(frac, msg)

    # ── Phase 1: Coarse sweep ────────────────────────────────────────────
    _report(0.0, "Phase 1: coarse rotation sweep…")
    total_coarse = count_rotations(coarse_step_deg)
    best_metric = float("inf")  # diameter (lower is more likely to fit)
    best_info: Optional[dict] = None
    found_fit = False

    for idx, R in enumerate(sample_rotations(coarse_step_deg)):
        rotated = hull.copy()
        rotated.apply_transform(R)
        bounds = rotated.bounds
        height = bounds[1][2] - bounds[0][2]

        if height > cyl_height:
            if idx % 500 == 0:
                _report(0.45 * (idx / total_coarse), f"Phase 1: {idx}/{total_coarse}")
            continue

        xy = rotated.vertices[:, :2]
        _, radius = minimal_enclosing_circle(xy)
        diameter = radius * 2.0

        if diameter <= cyl_diameter:
            # Fits! Record and break early for coarse phase
            best_info = {"diameter": diameter, "height": height, "rotation": R}
            found_fit = True
            break

        if diameter < best_metric:
            best_metric = diameter
            best_info = {"diameter": diameter, "height": height, "rotation": R}

        if idx % 500 == 0:
            _report(0.45 * (idx / total_coarse), f"Phase 1: {idx}/{total_coarse}")

    # ── Phase 2: Fine refinement ─────────────────────────────────────────
    if not found_fit and best_info is not None:
        _report(0.50, "Phase 2: refining best orientation…")
        euler = rotation_to_euler(best_info["rotation"])

        fine_rots = list(refine_rotations(euler, coarse_step_deg, fine_step_deg))
        total_fine = len(fine_rots)

        for idx, R in enumerate(fine_rots):
            rotated = hull.copy()
            rotated.apply_transform(R)
            bounds = rotated.bounds
            height = bounds[1][2] - bounds[0][2]

            if height > cyl_height:
                continue

            xy = rotated.vertices[:, :2]
            _, radius = minimal_enclosing_circle(xy)
            diameter = radius * 2.0

            if diameter <= cyl_diameter:
                best_info = {"diameter": diameter, "height": height, "rotation": R}
                found_fit = True
                break

            if diameter < best_metric:
                best_metric = diameter
                best_info = {"diameter": diameter, "height": height, "rotation": R}

            if idx % 200 == 0:
                _report(
                    0.50 + 0.45 * (idx / total_fine),
                    f"Phase 2: {idx}/{total_fine}",
                )

    _report(1.0, "Analysis complete.")

    result = ChokeResult(
        name=name,
        fits=found_fit,
        diameter_mm=best_info["diameter"] if best_info else None,
        height_mm=best_info["height"] if best_info else None,
        rotation=best_info["rotation"] if best_info else None,
        standard=standard,
    )

    # ── Cache store ──────────────────────────────────────────────────────
    if use_cache:
        _cache[key] = result

    return result
