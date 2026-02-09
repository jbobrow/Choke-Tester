"""
Tests for 3MF loading.

Creates minimal in-memory .3mf archives for testing.
"""

import io
import zipfile
import tempfile
import os
import pytest

from integrations.read_3mf import load_3mf_objects


# ── Helper to build a minimal .3mf in memory ────────────────────────────────

MINIMAL_MODEL_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
       unit="millimeter">
  <resources>
    <object id="1" name="TestCube" type="model">
      <mesh>
        <vertices>
          <vertex x="0" y="0" z="0"/>
          <vertex x="10" y="0" z="0"/>
          <vertex x="10" y="10" z="0"/>
          <vertex x="0" y="10" z="0"/>
          <vertex x="0" y="0" z="10"/>
          <vertex x="10" y="0" z="10"/>
          <vertex x="10" y="10" z="10"/>
          <vertex x="0" y="10" z="10"/>
        </vertices>
        <triangles>
          <triangle v1="0" v2="1" v3="2"/>
          <triangle v1="0" v2="2" v3="3"/>
          <triangle v1="4" v2="6" v3="5"/>
          <triangle v1="4" v2="7" v3="6"/>
          <triangle v1="0" v2="4" v3="5"/>
          <triangle v1="0" v2="5" v3="1"/>
          <triangle v1="1" v2="5" v3="6"/>
          <triangle v1="1" v2="6" v3="2"/>
          <triangle v1="2" v2="6" v3="7"/>
          <triangle v1="2" v2="7" v3="3"/>
          <triangle v1="3" v2="7" v3="4"/>
          <triangle v1="3" v2="4" v3="0"/>
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1"/>
  </build>
</model>
"""


def _write_temp_3mf(model_xml: str) -> str:
    """Write a temporary .3mf file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".3mf")
    os.close(fd)
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("3D/3dmodel.model", model_xml)
    return path


class TestLoad3MF:
    def test_loads_single_object(self):
        path = _write_temp_3mf(MINIMAL_MODEL_XML)
        try:
            objs = load_3mf_objects(path)
            assert len(objs) == 1
            assert objs[0].name == "TestCube"
            assert objs[0].object_id == "1"
            assert len(objs[0].mesh.vertices) == 8
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_3mf_objects("/nonexistent/file.3mf")

    def test_with_transform(self):
        xml = MINIMAL_MODEL_XML.replace(
            '<item objectid="1"/>',
            '<item objectid="1" transform="1 0 0 100 0 1 0 200 0 0 1 300"/>',
        )
        path = _write_temp_3mf(xml)
        try:
            objs = load_3mf_objects(path)
            assert len(objs) == 1
            # Vertices should be translated
            v = objs[0].mesh.vertices
            assert v[:, 0].min() >= 99  # original 0 + 100 translation
        finally:
            os.unlink(path)

    def test_bambu_component_indirection(self):
        """
        Bambu Studio .3mf files wrap meshes in component containers:
          build item → container object (no mesh) → component → leaf object (mesh)
        """
        xml = """\
<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
       unit="millimeter">
  <resources>
    <object id="1" name="LeafCube" type="model">
      <mesh>
        <vertices>
          <vertex x="0" y="0" z="0"/>
          <vertex x="10" y="0" z="0"/>
          <vertex x="10" y="10" z="0"/>
          <vertex x="0" y="10" z="0"/>
          <vertex x="0" y="0" z="10"/>
          <vertex x="10" y="0" z="10"/>
          <vertex x="10" y="10" z="10"/>
          <vertex x="0" y="10" z="10"/>
        </vertices>
        <triangles>
          <triangle v1="0" v2="1" v3="2"/>
          <triangle v1="0" v2="2" v3="3"/>
          <triangle v1="4" v2="6" v3="5"/>
          <triangle v1="4" v2="7" v3="6"/>
          <triangle v1="0" v2="4" v3="5"/>
          <triangle v1="0" v2="5" v3="1"/>
          <triangle v1="1" v2="5" v3="6"/>
          <triangle v1="1" v2="6" v3="2"/>
          <triangle v1="2" v2="6" v3="7"/>
          <triangle v1="2" v2="7" v3="3"/>
          <triangle v1="3" v2="7" v3="4"/>
          <triangle v1="3" v2="4" v3="0"/>
        </triangles>
      </mesh>
    </object>
    <object id="5" name="Container" type="model">
      <components>
        <component objectid="1" transform="1 0 0 50 0 1 0 0 0 0 1 0"/>
      </components>
    </object>
  </resources>
  <build>
    <item objectid="5"/>
  </build>
</model>
"""
        path = _write_temp_3mf(xml)
        try:
            objs = load_3mf_objects(path)
            assert len(objs) == 1
            assert objs[0].name == "LeafCube"
            # Component transform shifts X by 50
            v = objs[0].mesh.vertices
            assert v[:, 0].min() >= 49
        finally:
            os.unlink(path)

    def test_multiple_components(self):
        """Container with two component references to the same leaf mesh."""
        xml = """\
<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
       unit="millimeter">
  <resources>
    <object id="1" name="SharedCube" type="model">
      <mesh>
        <vertices>
          <vertex x="0" y="0" z="0"/>
          <vertex x="5" y="0" z="0"/>
          <vertex x="5" y="5" z="0"/>
          <vertex x="0" y="5" z="0"/>
          <vertex x="0" y="0" z="5"/>
          <vertex x="5" y="0" z="5"/>
          <vertex x="5" y="5" z="5"/>
          <vertex x="0" y="5" z="5"/>
        </vertices>
        <triangles>
          <triangle v1="0" v2="1" v3="2"/>
          <triangle v1="0" v2="2" v3="3"/>
          <triangle v1="4" v2="6" v3="5"/>
          <triangle v1="4" v2="7" v3="6"/>
          <triangle v1="0" v2="4" v3="5"/>
          <triangle v1="0" v2="5" v3="1"/>
          <triangle v1="1" v2="5" v3="6"/>
          <triangle v1="1" v2="6" v3="2"/>
          <triangle v1="2" v2="6" v3="7"/>
          <triangle v1="2" v2="7" v3="3"/>
          <triangle v1="3" v2="7" v3="4"/>
          <triangle v1="3" v2="4" v3="0"/>
        </triangles>
      </mesh>
    </object>
    <object id="10" type="model">
      <components>
        <component objectid="1"/>
        <component objectid="1" transform="1 0 0 20 0 1 0 0 0 0 1 0"/>
      </components>
    </object>
  </resources>
  <build>
    <item objectid="10"/>
  </build>
</model>
"""
        path = _write_temp_3mf(xml)
        try:
            objs = load_3mf_objects(path)
            assert len(objs) == 2  # same mesh, two instances
        finally:
            os.unlink(path)
