"""
Welzl's algorithm for computing the minimal enclosing circle of a 2D point set.

Handles degenerate cases (collinear points, duplicate points, single points)
gracefully.
"""

import numpy as np
from typing import Tuple

# Type alias
Circle = Tuple[np.ndarray, float]  # (center_xy, radius)


def minimal_enclosing_circle(points: np.ndarray) -> Circle:
    """
    Compute the smallest circle enclosing all given 2D points.

    Uses the randomised Welzl algorithm (expected O(n) time).

    Parameters
    ----------
    points : array-like, shape (N, 2)
        2D coordinates.

    Returns
    -------
    center : ndarray, shape (2,)
    radius : float
    """
    pts = np.asarray(points, dtype=np.float64).copy()

    if len(pts) == 0:
        return np.zeros(2), 0.0
    if len(pts) == 1:
        return pts[0].copy(), 0.0
    if len(pts) == 2:
        return _circle_from_2(pts[0], pts[1])

    # Shuffle for expected linear time
    rng = np.random.default_rng(42)
    rng.shuffle(pts)

    center, radius = _circle_from_2(pts[0], pts[1])

    for i in range(2, len(pts)):
        if _dist(pts[i], center) > radius + 1e-10:
            center, radius = _circle_with_point(pts[:i], pts[i])

    return center, radius


def _circle_with_point(pts: np.ndarray, p: np.ndarray) -> Circle:
    """Smallest enclosing circle where *p* must lie on the boundary."""
    center, radius = _circle_from_2(pts[0], p)

    for j in range(1, len(pts)):
        if _dist(pts[j], center) > radius + 1e-10:
            center, radius = _circle_with_two_points(pts[:j], pts[j], p)

    return center, radius


def _circle_with_two_points(
    pts: np.ndarray, q: np.ndarray, p: np.ndarray
) -> Circle:
    """Smallest enclosing circle where *p* and *q* must lie on the boundary."""
    center, radius = _circle_from_2(p, q)

    for k in range(len(pts)):
        if _dist(pts[k], center) > radius + 1e-10:
            center, radius = _circle_from_3(p, q, pts[k])

    return center, radius


# ── Primitive constructors ───────────────────────────────────────────────────

def _circle_from_2(a: np.ndarray, b: np.ndarray) -> Circle:
    center = (a + b) / 2.0
    radius = _dist(a, b) / 2.0
    return center, radius


def _circle_from_3(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> Circle:
    """
    Circle through three points. Handles the degenerate (collinear) case
    by falling back to the diameter of the two farthest points.
    """
    A = b - a
    B = c - a
    cross = A[0] * B[1] - A[1] * B[0]

    if abs(cross) < 1e-12:
        # Collinear — return circle on the two most distant points
        return _collinear_fallback(a, b, c)

    d = 2.0 * cross
    ux = (B[1] * np.dot(A, A) - A[1] * np.dot(B, B)) / d
    uy = (A[0] * np.dot(B, B) - B[0] * np.dot(A, A)) / d
    center = a + np.array([ux, uy])
    radius = _dist(center, a)
    return center, radius


def _collinear_fallback(
    a: np.ndarray, b: np.ndarray, c: np.ndarray
) -> Circle:
    """When three points are collinear, use the pair farthest apart."""
    d_ab = _dist(a, b)
    d_ac = _dist(a, c)
    d_bc = _dist(b, c)
    if d_ab >= d_ac and d_ab >= d_bc:
        return _circle_from_2(a, b)
    if d_ac >= d_bc:
        return _circle_from_2(a, c)
    return _circle_from_2(b, c)


def _dist(p: np.ndarray, q: np.ndarray) -> float:
    return float(np.linalg.norm(p - q))
