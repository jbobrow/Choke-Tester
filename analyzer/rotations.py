"""
Rotation sampling for choke-test analysis.

Two-phase strategy:
  1. Coarse sweep (configurable, default 15°) over the full rotation space.
  2. Fine refinement (configurable, default 3°) around the most promising
     orientation found in phase 1.

This dramatically reduces computation while still finding the orientation
that minimises the enclosing cylinder.
"""

import numpy as np
from typing import Generator, Tuple

# Type alias — 4×4 homogeneous transformation matrix
Mat4 = np.ndarray


def euler_matrix(rx: float, ry: float, rz: float) -> Mat4:
    """Build a 4×4 rotation matrix from Euler angles (radians, XYZ order)."""
    cx, sx = np.cos(rx), np.sin(rx)
    cy, sy = np.cos(ry), np.sin(ry)
    cz, sz = np.cos(rz), np.sin(rz)

    Rx = np.array([[1, 0,  0,  0],
                    [0, cx, -sx, 0],
                    [0, sx,  cx, 0],
                    [0, 0,   0,  1]], dtype=np.float64)

    Ry = np.array([[ cy, 0, sy, 0],
                    [  0, 1,  0, 0],
                    [-sy, 0, cy, 0],
                    [  0, 0,  0, 1]], dtype=np.float64)

    Rz = np.array([[cz, -sz, 0, 0],
                    [sz,  cz, 0, 0],
                    [ 0,   0, 1, 0],
                    [ 0,   0, 0, 1]], dtype=np.float64)

    return Rz @ Ry @ Rx


def sample_rotations(step_deg: float = 15) -> Generator[Mat4, None, None]:
    """
    Yield rotation matrices covering the rotation space at *step_deg*
    increments over [0, π) for each Euler axis.
    """
    step = np.deg2rad(step_deg)
    for rx in np.arange(0, np.pi, step):
        for ry in np.arange(0, np.pi, step):
            for rz in np.arange(0, np.pi, step):
                yield euler_matrix(rx, ry, rz)


def count_rotations(step_deg: float = 15) -> int:
    """Return how many rotations a given step size produces."""
    n = len(np.arange(0, np.pi, np.deg2rad(step_deg)))
    return n ** 3


def refine_rotations(
    best_euler: Tuple[float, float, float],
    coarse_step_deg: float = 15,
    fine_step_deg: float = 3,
) -> Generator[Mat4, None, None]:
    """
    Yield rotation matrices in a fine grid centred on *best_euler*.

    The search range is ±coarse_step_deg around the best orientation,
    sampled at *fine_step_deg* intervals.
    """
    rx0, ry0, rz0 = best_euler
    half = np.deg2rad(coarse_step_deg)
    fine = np.deg2rad(fine_step_deg)

    for rx in np.arange(rx0 - half, rx0 + half + 1e-9, fine):
        for ry in np.arange(ry0 - half, ry0 + half + 1e-9, fine):
            for rz in np.arange(rz0 - half, rz0 + half + 1e-9, fine):
                yield euler_matrix(rx, ry, rz)


def rotation_to_euler(R: Mat4) -> Tuple[float, float, float]:
    """
    Extract approximate Euler angles (XYZ order) from a 4×4 rotation matrix.
    Used to seed the refinement phase.
    """
    sy = -R[2, 0]
    cy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)

    if cy > 1e-6:
        rx = np.arctan2(R[2, 1], R[2, 2])
        ry = np.arctan2(sy, cy)
        rz = np.arctan2(R[1, 0], R[0, 0])
    else:
        rx = np.arctan2(-R[1, 2], R[1, 1])
        ry = np.arctan2(sy, cy)
        rz = 0.0

    return (rx, ry, rz)
