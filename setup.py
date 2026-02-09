"""
Package setup — allows `pip install -e .` for development.
"""

from setuptools import setup, find_packages

setup(
    name="bambu-choke-check",
    version="1.0.0",
    description="Choke test safety checker for Bambu Studio 3D prints",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "trimesh>=3.21.0",
        "numpy>=1.24.0",
        "shapely>=2.0.0",
        "PySide6>=6.5.0",
        "reportlab>=4.0.0",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"],
    },
    entry_points={
        "console_scripts": [
            "choke-check=run:main",
        ],
    },
)
