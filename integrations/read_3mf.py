"""
Load meshes and metadata from Bambu Studio .3mf project files.

Primary strategy: use trimesh's built-in 3MF loader (handles the full
spec including production extensions, column-major transforms, and
multi-file references).

Fallback: manual XML parsing with component resolution for cases
where trimesh's loader doesn't return the expected results.
"""

import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import trimesh

from .transforms import parse_transform

# 3MF core namespace
NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}


@dataclass
class ThreeMFObject:
    """One printable object extracted from a .3mf project."""
    name: str
    mesh: trimesh.Trimesh
    object_id: str


def load_3mf_objects(path: Union[str, Path]) -> List[ThreeMFObject]:
    """
    Parse a .3mf file and return a list of ``ThreeMFObject`` instances.

    Tries trimesh's native loader first (most robust), then falls back
    to manual XML parsing if trimesh returns no geometry.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # ── Strategy 1: trimesh native loader ────────────────────────────────
    objects = _load_via_trimesh(path)
    if objects:
        return objects

    # ── Strategy 2: manual XML with component resolution ─────────────────
    objects = _load_via_xml(path)
    if objects:
        return objects

    raise ValueError(
        f"Could not extract any meshes from {path.name}. "
        f"The file may be empty or use an unsupported format variant."
    )


def _load_via_trimesh(path: Path) -> List[ThreeMFObject]:
    """Use trimesh's built-in 3MF support."""
    try:
        loaded = trimesh.load(str(path))
    except Exception:
        return []

    objects: List[ThreeMFObject] = []

    if isinstance(loaded, trimesh.Scene):
        for idx, (name, geom) in enumerate(loaded.geometry.items()):
            if isinstance(geom, trimesh.Trimesh) and len(geom.vertices) > 0:
                # Apply the scene graph transform for this geometry
                try:
                    transform = loaded.graph.get(name)[0]
                    mesh = geom.copy()
                    mesh.apply_transform(transform)
                except Exception:
                    mesh = geom.copy()
                objects.append(ThreeMFObject(
                    name=name,
                    mesh=mesh,
                    object_id=str(idx),
                ))
    elif isinstance(loaded, trimesh.Trimesh) and len(loaded.vertices) > 0:
        objects.append(ThreeMFObject(
            name=path.stem,
            mesh=loaded,
            object_id="0",
        ))

    return objects


def _load_via_xml(path: Path) -> List[ThreeMFObject]:
    """Manual XML parsing with recursive component resolution."""
    objects: List[ThreeMFObject] = []

    try:
        with zipfile.ZipFile(path, "r") as zf:
            model_path = _find_model_path(zf)
            root = ET.fromstring(zf.read(model_path))
    except Exception:
        return objects

    resources = root.find("m:resources", NS)
    build = root.find("m:build", NS)

    if resources is None or build is None:
        return objects

    # Index ALL object definitions by id
    all_objects: Dict[str, ET.Element] = {}
    for obj in resources.findall("m:object", NS):
        all_objects[obj.attrib.get("id", "")] = obj

    # Walk build items and recursively resolve components
    for item in build.findall("m:item", NS):
        obj_id = item.attrib.get("objectid", "")
        item_transform = parse_transform(item.attrib.get("transform"))

        resolved = _resolve_object(obj_id, all_objects, item_transform)
        objects.extend(resolved)

    return objects


def _resolve_object(
    obj_id: str,
    all_objects: Dict[str, ET.Element],
    parent_transform: np.ndarray,
) -> List[ThreeMFObject]:
    """
    Recursively resolve an object.  If it contains a <mesh>, return it.
    If it contains <components>, recurse into each child component.
    """
    obj_def = all_objects.get(obj_id)
    if obj_def is None:
        return []

    name = obj_def.attrib.get("name", f"Object {obj_id}")
    results: List[ThreeMFObject] = []

    mesh_tag = obj_def.find("m:mesh", NS)
    components_tag = obj_def.find("m:components", NS)

    # ── Leaf object: has mesh data directly ──────────────────────────────
    if mesh_tag is not None:
        mesh = _build_mesh(mesh_tag)
        if len(mesh.vertices) > 0:
            mesh.apply_transform(parent_transform)
            results.append(ThreeMFObject(name=name, mesh=mesh, object_id=obj_id))

    # ── Container object: has <components> referencing children ──────────
    if components_tag is not None:
        for comp in components_tag.findall("m:component", NS):
            child_id = comp.attrib.get("objectid", "")
            comp_transform = parse_transform(comp.attrib.get("transform"))
            combined = parent_transform @ comp_transform
            results.extend(
                _resolve_object(child_id, all_objects, combined)
            )

    return results


# ── Helpers ──────────────────────────────────────────────────────────────────

def _find_model_path(zf: zipfile.ZipFile) -> str:
    """Locate the model XML inside the ZIP; handles variant paths."""
    candidates = [
        "3D/3dmodel.model",
        "3d/3dmodel.model",
        "3D/3DModel.model",
    ]
    names = zf.namelist()
    for c in candidates:
        if c in names:
            return c
    for n in names:
        if n.lower().endswith(".model"):
            return n
    raise KeyError("No 3D model file found in the .3mf archive.")


def _build_mesh(mesh_tag: ET.Element) -> trimesh.Trimesh:
    """Build a trimesh from a 3MF <mesh> element."""
    verts_tag = mesh_tag.find("m:vertices", NS)
    tris_tag = mesh_tag.find("m:triangles", NS)

    if verts_tag is None or tris_tag is None:
        return trimesh.Trimesh()

    vertices = [
        [float(v.attrib["x"]), float(v.attrib["y"]), float(v.attrib["z"])]
        for v in verts_tag.findall("m:vertex", NS)
    ]
    faces = [
        [int(t.attrib["v1"]), int(t.attrib["v2"]), int(t.attrib["v3"])]
        for t in tris_tag.findall("m:triangle", NS)
    ]

    return trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
