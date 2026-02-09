"""
Utilities for parsing 3MF transform attributes into 4×4 matrices.
"""

from typing import Optional

import numpy as np


def parse_transform(transform_str: Optional[str]) -> np.ndarray:
    """
    Parse a 3MF ``transform`` attribute string into a 4×4 homogeneous
    transformation matrix.

    The 3MF spec stores transforms as 12 floats in *row-major* order
    (3 rows × 4 columns), with an implicit fourth row [0 0 0 1].

    Returns the identity matrix when *transform_str* is ``None`` or empty.
    """
    if not transform_str or not transform_str.strip():
        return np.eye(4, dtype=np.float64)

    values = list(map(float, transform_str.split()))

    if len(values) == 12:
        matrix = np.array(
            [
                [values[0], values[1], values[2], values[3]],
                [values[4], values[5], values[6], values[7]],
                [values[8], values[9], values[10], values[11]],
                [0.0,       0.0,       0.0,        1.0],
            ],
            dtype=np.float64,
        )
    elif len(values) == 16:
        matrix = np.array(values, dtype=np.float64).reshape(4, 4)
    else:
        raise ValueError(
            f"Expected 12 or 16 floats in transform, got {len(values)}: "
            f"{transform_str!r}"
        )

    return matrix
