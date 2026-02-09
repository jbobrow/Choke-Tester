"""
Tests for the minimal enclosing circle (Welzl's algorithm).
"""

import numpy as np
import pytest

from analyzer.enclosing_circle import minimal_enclosing_circle


class TestMinimalEnclosingCircle:
    """Core algorithm tests."""

    def test_empty_set(self):
        center, radius = minimal_enclosing_circle(np.empty((0, 2)))
        assert radius == 0.0
        np.testing.assert_array_equal(center, [0.0, 0.0])

    def test_single_point(self):
        pts = np.array([[3.0, 4.0]])
        center, radius = minimal_enclosing_circle(pts)
        assert radius == 0.0
        np.testing.assert_allclose(center, [3.0, 4.0])

    def test_two_points(self):
        pts = np.array([[0.0, 0.0], [10.0, 0.0]])
        center, radius = minimal_enclosing_circle(pts)
        np.testing.assert_allclose(center, [5.0, 0.0], atol=1e-10)
        assert abs(radius - 5.0) < 1e-10

    def test_equilateral_triangle(self):
        # Equilateral triangle with side 2, centred roughly at origin
        s = 2.0
        pts = np.array([
            [0.0, 0.0],
            [s, 0.0],
            [s / 2, s * np.sqrt(3) / 2],
        ])
        center, radius = minimal_enclosing_circle(pts)
        # Circumradius = s / sqrt(3)
        expected_r = s / np.sqrt(3)
        assert abs(radius - expected_r) < 1e-8

    def test_square(self):
        pts = np.array([
            [0.0, 0.0], [1.0, 0.0],
            [1.0, 1.0], [0.0, 1.0],
        ])
        center, radius = minimal_enclosing_circle(pts)
        np.testing.assert_allclose(center, [0.5, 0.5], atol=1e-8)
        expected_r = np.sqrt(2) / 2
        assert abs(radius - expected_r) < 1e-8

    def test_collinear_points(self):
        """Degenerate case: all points on a line."""
        pts = np.array([[0.0, 0.0], [5.0, 0.0], [10.0, 0.0]])
        center, radius = minimal_enclosing_circle(pts)
        np.testing.assert_allclose(center, [5.0, 0.0], atol=1e-8)
        assert abs(radius - 5.0) < 1e-8

    def test_duplicate_points(self):
        pts = np.array([
            [1.0, 1.0], [1.0, 1.0], [1.0, 1.0], [1.0, 1.0],
        ])
        center, radius = minimal_enclosing_circle(pts)
        assert radius < 1e-8  # essentially zero
        np.testing.assert_allclose(center, [1.0, 1.0], atol=1e-8)

    def test_many_random_points_containment(self):
        """All points must lie inside (or on) the returned circle."""
        rng = np.random.default_rng(123)
        pts = rng.standard_normal((200, 2)) * 50
        center, radius = minimal_enclosing_circle(pts)
        dists = np.linalg.norm(pts - center, axis=1)
        assert np.all(dists <= radius + 1e-6)

    def test_circle_on_boundary(self):
        """Points on a known circle should yield that exact circle."""
        angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)
        r = 15.0
        pts = np.column_stack([r * np.cos(angles), r * np.sin(angles)])
        center, radius = minimal_enclosing_circle(pts)
        np.testing.assert_allclose(center, [0.0, 0.0], atol=1e-6)
        assert abs(radius - r) < 1e-6
