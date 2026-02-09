"""
Visual preview widget with two tabs:
  1. 2D Views  — top-down (XY) and side (XZ) projections
  2. 3D View   — interactive orbit with reset-view button

Whole-object colouring: red = choking hazard, grey = safe.
The convex hull is shown as a subtle dashed outline.
The 3D mesh is decimated to MAX_3D_FACES for smooth interaction.
"""

import numpy as np
from typing import Optional, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QPushButton,
)
from PySide6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle, Polygon
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from scipy.spatial import ConvexHull

from analyzer.choke_check import ChokeResult
from analyzer.enclosing_circle import minimal_enclosing_circle


# ── Colours ──────────────────────────────────────────────────────────────────
CYL_EDGE    = "#1565C0"
CYL_FILL    = "#E3F2FD"
SAFE_FILL   = "#CFD8DC"       # light grey — safe
SAFE_EDGE   = "#546E7A"
HAZARD_FILL = "#FFCDD2"       # light red  — choking hazard
HAZARD_EDGE = "#C62828"
HULL_EDGE   = "#90A4AE"       # subtle hull outline

# Maximum triangle count for the 3D view (keeps orbit responsive)
MAX_3D_FACES = 1500

# Home camera position
HOME_ELEV = 25
HOME_AZIM = -45


def _centre_and_floor(verts: np.ndarray) -> np.ndarray:
    """Shift vertices so the object is centred on XY and sits at Z=0."""
    out = verts.copy()
    out[:, 2] -= out[:, 2].min()
    out[:, 0] -= (out[:, 0].max() + out[:, 0].min()) / 2
    out[:, 1] -= (out[:, 1].max() + out[:, 1].min()) / 2
    return out


def _decimate_mesh(verts, faces, max_faces):
    """
    Reduce face count for faster 3D rendering.
    Uses uniform random sampling — fast and good enough for preview.
    """
    n = len(faces)
    if n <= max_faces:
        return verts, faces
    indices = np.random.default_rng(42).choice(n, max_faces, replace=False)
    return verts, faces[indices]


def _obj_colours(is_hazard: bool):
    """Return (fill, edge) colour pair for the whole object."""
    if is_hazard:
        return HAZARD_FILL, HAZARD_EDGE
    return SAFE_FILL, SAFE_EDGE


class PreviewWidget(QWidget):
    """Tabbed preview: 2D projections + interactive 3D view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ax3d = None          # keep ref for reset-view
        self._3d_limits = None     # (max_extent, max_z) for reset
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("Select an object to preview")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; padding: 4px;")
        layout.addWidget(self.title_label)

        self.tabs = QTabWidget()

        # Tab 1: 2D projections
        self.fig_2d = Figure(figsize=(6, 3.5), dpi=100)
        self.fig_2d.set_facecolor("#FAFAFA")
        self.canvas_2d = FigureCanvas(self.fig_2d)
        self.tabs.addTab(self.canvas_2d, "2D Views")

        # Tab 2: interactive 3D  (canvas + reset button)
        tab3d = QWidget()
        tab3d_layout = QVBoxLayout(tab3d)
        tab3d_layout.setContentsMargins(0, 0, 0, 0)

        # Button bar
        btn_bar = QHBoxLayout()
        btn_bar.addStretch()
        self.btn_reset = QPushButton("Reset View")
        self.btn_reset.setFixedWidth(100)
        self.btn_reset.setToolTip("Return to default camera angle")
        self.btn_reset.clicked.connect(self._reset_3d_view)
        btn_bar.addWidget(self.btn_reset)
        tab3d_layout.addLayout(btn_bar)

        self.fig_3d = Figure(figsize=(5, 4), dpi=100)
        self.fig_3d.set_facecolor("#FAFAFA")
        self.canvas_3d = FigureCanvas(self.fig_3d)
        tab3d_layout.addWidget(self.canvas_3d)

        self.tabs.addTab(tab3d, "3D View")
        layout.addWidget(self.tabs)

    # ── Public API ───────────────────────────────────────────────────────

    def show_result(self, result: ChokeResult, mesh=None):
        """
        Render the preview.  *mesh* is the **original** mesh (not hull).
        """
        self.title_label.setText(result.name)

        cyl_r = result.standard.diameter_mm / 2.0
        cyl_h = result.standard.height_mm

        if mesh is not None and result.rotation is not None:
            # Original mesh — rotated to the analysis orientation
            orig = mesh.copy()
            orig.apply_transform(result.rotation)
            orig_verts = orig.vertices
            orig_faces = orig.faces

            # Convex hull — for subtle overlay
            hull = orig.convex_hull
            hull_verts = hull.vertices
            hull_faces = hull.faces
        else:
            orig_verts = orig_faces = None
            hull_verts = hull_faces = None

        self._draw_2d(cyl_r, cyl_h, orig_verts, orig_faces,
                       hull_verts, result)
        self._draw_3d(cyl_r, cyl_h, orig_verts, orig_faces,
                       hull_verts, hull_faces, result)

    def clear_preview(self):
        self.fig_2d.clear()
        self.fig_3d.clear()
        self._ax3d = None
        self.title_label.setText("Select an object to preview")
        self.canvas_2d.draw()
        self.canvas_3d.draw()

    # ══════════════════════════════════════════════════════════════════════
    # 2D VIEWS
    # ══════════════════════════════════════════════════════════════════════

    def _draw_2d(self, cyl_r, cyl_h, orig_v, orig_f, hull_v, result):
        self.fig_2d.clear()
        ax_top  = self.fig_2d.add_subplot(1, 2, 1)
        ax_side = self.fig_2d.add_subplot(1, 2, 2)

        self._draw_top(ax_top, cyl_r, orig_v, orig_f, hull_v, result)
        self._draw_side(ax_side, cyl_r, cyl_h, orig_v, orig_f, hull_v, result)

        self.fig_2d.tight_layout(pad=1.5)
        self.canvas_2d.draw()

    # ── Top view (XY) ────────────────────────────────────────────────────

    def _draw_top(self, ax, cyl_r, orig_v, orig_f, hull_v, result):
        ax.set_aspect("equal")
        fill, edge = _obj_colours(result.fits)

        # Cylinder
        ax.add_patch(Circle(
            (0, 0), cyl_r,
            fill=True, facecolor=CYL_FILL, edgecolor=CYL_EDGE,
            linewidth=2, linestyle="--", alpha=0.4,
            label="Cylinder \u00d8{:.1f}mm".format(cyl_r * 2),
        ))

        enc_r = cyl_r  # fallback for margin calc
        if orig_v is not None and orig_f is not None:
            xy = orig_v[:, :2]
            center, enc_r = minimal_enclosing_circle(xy)
            offset = center

            # --- Subtle convex-hull outline (behind the mesh) ---
            if hull_v is not None:
                hxy = hull_v[:, :2] - offset
                try:
                    ch = ConvexHull(hxy)
                    hull_poly = Polygon(
                        hxy[ch.vertices], closed=True,
                        facecolor="none", edgecolor=HULL_EDGE,
                        linewidth=1, linestyle=":", alpha=0.5, zorder=2,
                    )
                    ax.add_patch(hull_poly)
                except Exception:
                    pass

            # --- Original mesh triangles projected to XY ---
            tris_xy = orig_v[orig_f][:, :, :2] - offset
            coll = PolyCollection(
                tris_xy,
                facecolors=fill, edgecolors=edge,
                linewidths=0.3, alpha=0.7, zorder=3,
                label="Object \u00d8{:.1f}mm".format(enc_r * 2),
            )
            ax.add_collection(coll)

        colour = "#B71C1C" if result.fits else "#1B5E20"
        ax.set_title("Top View (XY)", fontsize=9, color=colour, fontweight="bold")
        margin = max(cyl_r, enc_r) * 1.5
        ax.set_xlim(-margin, margin)
        ax.set_ylim(-margin, margin)
        ax.legend(fontsize=7, loc="upper right")
        ax.grid(True, alpha=0.2)

    # ── Side view (XZ) ───────────────────────────────────────────────────

    def _draw_side(self, ax, cyl_r, cyl_h, orig_v, orig_f, hull_v, result):
        ax.set_aspect("equal")
        fill, edge = _obj_colours(result.fits)

        # Cylinder
        ax.add_patch(Rectangle(
            (-cyl_r, 0), cyl_r * 2, cyl_h,
            fill=True, facecolor=CYL_FILL, edgecolor=CYL_EDGE,
            linewidth=2, linestyle="--", alpha=0.4,
            label="Cylinder {:.1f}mm".format(cyl_h),
        ))

        obj_h = 0
        if orig_v is not None and orig_f is not None:
            xz = orig_v[:, [0, 2]].copy()
            z_min = xz[:, 1].min()
            xz[:, 1] -= z_min
            cx = (xz[:, 0].max() + xz[:, 0].min()) / 2
            xz[:, 0] -= cx
            obj_h = xz[:, 1].max()

            # --- Subtle hull outline ---
            if hull_v is not None:
                hxz = hull_v[:, [0, 2]].copy()
                hxz[:, 1] -= z_min
                hxz[:, 0] -= cx
                try:
                    ch = ConvexHull(hxz)
                    hull_poly = Polygon(
                        hxz[ch.vertices], closed=True,
                        facecolor="none", edgecolor=HULL_EDGE,
                        linewidth=1, linestyle=":", alpha=0.5, zorder=2,
                    )
                    ax.add_patch(hull_poly)
                except Exception:
                    pass

            # --- Original mesh triangles projected to XZ ---
            tris_xz = np.empty((len(orig_f), 3, 2))
            for i, f in enumerate(orig_f):
                tri = orig_v[f]
                tris_xz[i, :, 0] = tri[:, 0] - cx
                tris_xz[i, :, 1] = tri[:, 2] - z_min

            coll = PolyCollection(
                tris_xz,
                facecolors=fill, edgecolors=edge,
                linewidths=0.3, alpha=0.7, zorder=3,
                label="Object h={:.1f}mm".format(obj_h),
            )
            ax.add_collection(coll)

        colour = "#B71C1C" if result.fits else "#1B5E20"
        ax.set_title("Side View (XZ)", fontsize=9, color=colour, fontweight="bold")
        margin_x = cyl_r * 1.5
        margin_y = max(cyl_h, obj_h) * 1.2
        ax.set_xlim(-margin_x, margin_x)
        ax.set_ylim(-5, margin_y)
        ax.legend(fontsize=7, loc="upper right")
        ax.grid(True, alpha=0.2)

    # ══════════════════════════════════════════════════════════════════════
    # 3D VIEW
    # ══════════════════════════════════════════════════════════════════════

    def _reset_3d_view(self):
        """Reset the 3D camera to the home position."""
        if self._ax3d is not None:
            self._ax3d.view_init(elev=HOME_ELEV, azim=HOME_AZIM)
            if self._3d_limits:
                me, mz = self._3d_limits
                self._ax3d.set_xlim(-me, me)
                self._ax3d.set_ylim(-me, me)
                self._ax3d.set_zlim(0, mz)
            try:
                self.canvas_3d.draw()
            except Exception:
                pass

    def _draw_3d(self, cyl_r, cyl_h, orig_v, orig_f, hull_v, hull_f, result):
        self.fig_3d.clear()
        ax = self.fig_3d.add_subplot(111, projection="3d")
        self._ax3d = ax

        fill, edge = _obj_colours(result.fits)

        # --- Choke cylinder wireframe (lightweight) ---
        theta = np.linspace(0, 2 * np.pi, 40)
        for z in [0, cyl_h]:
            ax.plot(cyl_r * np.cos(theta), cyl_r * np.sin(theta), z,
                    color=CYL_EDGE, linewidth=1.2, alpha=0.5)
        for angle in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            ax.plot([cyl_r * np.cos(angle)] * 2,
                    [cyl_r * np.sin(angle)] * 2,
                    [0, cyl_h],
                    color=CYL_EDGE, linewidth=0.6, alpha=0.3)

        max_extent = cyl_r * 1.3
        max_z = cyl_h * 1.1

        if orig_v is not None and orig_f is not None:
            shifted = _centre_and_floor(orig_v)

            # --- Decimate for performance ---
            disp_v, disp_f = _decimate_mesh(shifted, orig_f, MAX_3D_FACES)

            # --- Subtle hull outline as edge lines (compatible with all mpl) ---
            if hull_v is not None and hull_f is not None:
                h_shifted = _centre_and_floor(hull_v)
                # Only draw a subset of hull edges to keep it light
                hull_step = max(1, len(hull_f) // 200)
                for face in hull_f[::hull_step]:
                    tri = h_shifted[face]
                    for i in range(3):
                        j = (i + 1) % 3
                        ax.plot(
                            [tri[i, 0], tri[j, 0]],
                            [tri[i, 1], tri[j, 1]],
                            [tri[i, 2], tri[j, 2]],
                            color=HULL_EDGE, linewidth=0.3,
                            alpha=0.15, linestyle=":",
                        )

            # --- Mesh faces — single colour for entire object ---
            try:
                mesh_coll = Poly3DCollection(
                    disp_v[disp_f],
                    alpha=0.85,
                )
                mesh_coll.set_facecolor(fill)
                mesh_coll.set_edgecolor(edge)
                mesh_coll.set_linewidth(0.25)
                ax.add_collection3d(mesh_coll)
            except Exception:
                # Fallback: wireframe only
                for f in disp_f:
                    tri = disp_v[f]
                    for i in range(3):
                        j = (i + 1) % 3
                        ax.plot(
                            [tri[i, 0], tri[j, 0]],
                            [tri[i, 1], tri[j, 1]],
                            [tri[i, 2], tri[j, 2]],
                            color=edge, linewidth=0.4, alpha=0.7,
                        )

            max_extent = max(
                max_extent,
                np.abs(shifted[:, 0]).max() * 1.1,
                np.abs(shifted[:, 1]).max() * 1.1,
            )
            max_z = max(max_z, shifted[:, 2].max() * 1.1)

        self._3d_limits = (max_extent, max_z)

        ax.set_xlim(-max_extent, max_extent)
        ax.set_ylim(-max_extent, max_extent)
        ax.set_zlim(0, max_z)
        ax.set_xlabel("X (mm)", fontsize=8)
        ax.set_ylabel("Y (mm)", fontsize=8)
        ax.set_zlabel("Z (mm)", fontsize=8)
        ax.tick_params(labelsize=7)

        colour = "#B71C1C" if result.fits else "#1B5E20"
        status = "CHOKING HAZARD" if result.fits else "SAFE"
        ax.set_title("{} \u2014 {}".format(result.name, status),
                     fontsize=10, color=colour, fontweight="bold")
        ax.view_init(elev=HOME_ELEV, azim=HOME_AZIM)

        self.fig_3d.tight_layout(pad=0.5)
        try:
            self.canvas_3d.draw()
        except Exception:
            # Graceful fallback
            self.fig_3d.clear()
            ax2 = self.fig_3d.add_subplot(111)
            ax2.text(0.5, 0.5, "3D preview unavailable\n(matplotlib compat issue)",
                     ha="center", va="center", fontsize=10, color="#999")
            ax2.set_axis_off()
            self.canvas_3d.draw()
