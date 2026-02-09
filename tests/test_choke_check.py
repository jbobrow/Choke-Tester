"""
Tests for the core choke-check analyser.
"""

import numpy as np
import trimesh
import pytest

from analyzer.choke_check import fits_choke_cylinder, clear_cache, ChokeResult
from analyzer.standards import US_CPSC, EU_EN71, custom_standard


def _make_box(x: float, y: float, z: float) -> trimesh.Trimesh:
    """Create a box mesh centred at the origin."""
    return trimesh.creation.box(extents=[x, y, z])


def _make_sphere(radius: float) -> trimesh.Trimesh:
    return trimesh.creation.icosphere(subdivisions=2, radius=radius)


class TestFitsChokeCylinder:
    def setup_method(self):
        clear_cache()

    # ── Obvious pass (large object) ──────────────────────────────────────

    def test_large_box_does_not_fit(self):
        mesh = _make_box(100, 100, 100)
        result = fits_choke_cylinder(mesh, standard=US_CPSC, name="BigBox")
        assert result.fits is False
        assert result.name == "BigBox"

    # ── Obvious fail (tiny object) ───────────────────────────────────────

    def test_tiny_sphere_fits(self):
        # 5mm radius sphere → diameter 10mm, well under 31.7mm
        mesh = _make_sphere(5.0)
        result = fits_choke_cylinder(mesh, standard=US_CPSC, name="TinySphere")
        assert result.fits is True
        assert result.diameter_mm is not None
        assert result.diameter_mm < US_CPSC.diameter_mm

    # ── Borderline cases ─────────────────────────────────────────────────

    def test_box_just_exceeds_diameter(self):
        # Box 35×35×10mm — diagonal = ~49.5mm > 31.7mm
        mesh = _make_box(35, 35, 10)
        result = fits_choke_cylinder(mesh, standard=US_CPSC, name="WideFlat")
        assert result.fits is False

    def test_tall_narrow_box_exceeds_height(self):
        # 10×10×100mm — fits in diameter but not height
        mesh = _make_box(10, 10, 100)
        result = fits_choke_cylinder(mesh, standard=US_CPSC, name="TallNarrow")
        # When standing upright it's too tall, but rotated on its side
        # the 100mm dimension becomes the diameter (too wide)
        assert result.fits is False

    # ── Standard switching ───────────────────────────────────────────────

    def test_medium_object_passes_us_fails_eu(self):
        # An object small enough for US but checked against larger EU cylinder
        mesh = _make_box(20, 20, 40)
        us_result = fits_choke_cylinder(mesh, standard=US_CPSC, name="MedBox")
        eu_result = fits_choke_cylinder(mesh, standard=EU_EN71, name="MedBox")
        # Under US (31.7mm dia): diagonal ~28mm fits, height 40mm < 57.1mm → fits
        # Under EU (44.5mm dia): same object also fits the larger cylinder
        assert us_result.fits is True
        assert eu_result.fits is True

    def test_custom_standard(self):
        std = custom_standard("Tiny", diameter_mm=10, height_mm=10)
        mesh = _make_box(5, 5, 5)
        result = fits_choke_cylinder(mesh, standard=std, name="SmallCube")
        assert result.fits is True
        assert result.standard.name == "Tiny"

    # ── Caching ──────────────────────────────────────────────────────────

    def test_cache_returns_same_result(self):
        mesh = _make_box(50, 50, 50)
        r1 = fits_choke_cylinder(mesh, standard=US_CPSC, name="Cached")
        r2 = fits_choke_cylinder(mesh, standard=US_CPSC, name="Cached")
        assert r1.fits == r2.fits
        assert r1.diameter_mm == r2.diameter_mm

    # ── Result dataclass ─────────────────────────────────────────────────

    def test_status_text(self):
        r_fail = ChokeResult("A", True, 10.0, 20.0, None, US_CPSC)
        assert "FAIL" in r_fail.status_text

        r_pass = ChokeResult("B", False, 50.0, 80.0, None, US_CPSC)
        assert "PASS" in r_pass.status_text
