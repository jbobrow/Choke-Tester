"""
Configurable safety standards for choke test cylinder dimensions.

Supports US CPSC, EU EN-71, and custom user-defined standards.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ChokeStandard:
    """Defines a choke test cylinder standard."""
    name: str
    diameter_mm: float
    height_mm: float
    description: str

    @property
    def radius_mm(self) -> float:
        return self.diameter_mm / 2.0


# ── Built-in standards ───────────────────────────────────────────────────────

US_CPSC = ChokeStandard(
    name="US CPSC (16 CFR 1501)",
    diameter_mm=31.7,
    height_mm=57.1,
    description=(
        "U.S. Consumer Product Safety Commission small-parts cylinder. "
        "Objects intended for children under 3 that fit entirely inside "
        "this cylinder are considered choking hazards."
    ),
)

EU_EN71 = ChokeStandard(
    name="EU EN-71",
    diameter_mm=44.5,
    height_mm=51.0,
    description=(
        "European Standard EN-71 small-parts cylinder for toy safety. "
        "Parts that fit inside are classified as choking hazards for "
        "children under 36 months."
    ),
)

# ── Registry ─────────────────────────────────────────────────────────────────

BUILTIN_STANDARDS: Dict[str, ChokeStandard] = {
    "us_cpsc": US_CPSC,
    "eu_en71": EU_EN71,
}

DEFAULT_STANDARD_KEY = "us_cpsc"


def get_standard(key: str) -> ChokeStandard:
    """Retrieve a built-in standard by key."""
    if key not in BUILTIN_STANDARDS:
        raise KeyError(
            f"Unknown standard '{key}'. "
            f"Available: {list(BUILTIN_STANDARDS.keys())}"
        )
    return BUILTIN_STANDARDS[key]


def custom_standard(
    name: str,
    diameter_mm: float,
    height_mm: float,
    description: str = "User-defined standard",
) -> ChokeStandard:
    """Create a custom choke test standard."""
    if diameter_mm <= 0 or height_mm <= 0:
        raise ValueError("Diameter and height must be positive values.")
    return ChokeStandard(
        name=name,
        diameter_mm=diameter_mm,
        height_mm=height_mm,
        description=description,
    )
