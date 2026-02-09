"""
Tests for rotation sampling and Euler angle utilities.
"""

import numpy as np
import pytest

from analyzer.rotations import (
    euler_matrix,
    sample_rotations,
    count_rotations,
    refine_rotations,
    rotation_to_euler,
)


class TestEulerMatrix:
    def test_identity(self):
        """Zero angles → identity matrix."""
        R = euler_matrix(0, 0, 0)
        np.testing.assert_allclose(R, np.eye(4), atol=1e-12)

    def test_90_deg_x(self):
        """90° about X should map Y→Z."""
        R = euler_matrix(np.pi / 2, 0, 0)
        v = R[:3, :3] @ np.array([0, 1, 0])
        np.testing.assert_allclose(v, [0, 0, 1], atol=1e-10)

    def test_90_deg_z(self):
        """90° about Z should map X→Y."""
        R = euler_matrix(0, 0, np.pi / 2)
        v = R[:3, :3] @ np.array([1, 0, 0])
        np.testing.assert_allclose(v, [0, 1, 0], atol=1e-10)

    def test_determinant(self):
        """Rotation matrix determinant should be +1."""
        R = euler_matrix(0.3, 0.7, 1.2)
        det = np.linalg.det(R[:3, :3])
        assert abs(det - 1.0) < 1e-10

    def test_orthogonality(self):
        """R^T @ R should equal I."""
        R = euler_matrix(0.5, 1.0, 1.5)
        product = R[:3, :3].T @ R[:3, :3]
        np.testing.assert_allclose(product, np.eye(3), atol=1e-10)


class TestSampleRotations:
    def test_count_matches(self):
        for step in [15, 30, 45]:
            count = count_rotations(step)
            rotations = list(sample_rotations(step))
            assert len(rotations) == count

    def test_all_valid_rotation_matrices(self):
        for R in sample_rotations(45):
            det = np.linalg.det(R[:3, :3])
            assert abs(det - 1.0) < 1e-8


class TestRefineRotations:
    def test_refinement_stays_near_seed(self):
        seed = (0.5, 0.5, 0.5)
        coarse = 15
        fine = 3
        half = np.deg2rad(coarse)

        for R in refine_rotations(seed, coarse, fine):
            euler = rotation_to_euler(R)
            for orig, refined in zip(seed, euler):
                assert abs(refined - orig) < half + 0.1  # small tolerance


class TestEulerRoundTrip:
    def test_roundtrip(self):
        """Build a rotation, extract Euler, rebuild — should match."""
        for rx, ry, rz in [(0.1, 0.2, 0.3), (1.0, 0.5, 0.8)]:
            R1 = euler_matrix(rx, ry, rz)
            ex, ey, ez = rotation_to_euler(R1)
            R2 = euler_matrix(ex, ey, ez)
            np.testing.assert_allclose(R1, R2, atol=1e-8)
