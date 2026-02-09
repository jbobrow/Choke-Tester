"""
Main application window.

Layout:
  ┌────────────────────────────────────────────────┐
  │  Menu bar  (File / Settings / Help)            │
  ├──────────────────────┬─────────────────────────┤
  │                      │                         │
  │    Results Table     │    Visual Preview        │
  │                      │                         │
  ├──────────────────────┴─────────────────────────┤
  │  Status bar / progress                         │
  └────────────────────────────────────────────────┘
"""

import os
from pathlib import Path
from typing import List, Optional

import trimesh
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QProgressBar,
    QLabel,
    QSplitter,
    QStatusBar,
)
from PySide6.QtCore import Qt, QThread, Signal, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from analyzer.choke_check import ChokeResult, fits_choke_cylinder, clear_cache
from analyzer.standards import (
    ChokeStandard,
    BUILTIN_STANDARDS,
    DEFAULT_STANDARD_KEY,
)
from integrations.read_3mf import load_3mf_objects
from .results_table import ResultsTable
from .settings_dialog import SettingsDialog
from .preview_widget import PreviewWidget


# ── Background worker ────────────────────────────────────────────────────────

class AnalysisWorker(QThread):
    """Run choke analysis in a background thread so the UI stays responsive."""
    progress = Signal(float, str)
    result_ready = Signal(object, object)   # (ChokeResult, mesh)
    finished_all = Signal()

    def __init__(self, items, standard):
        super().__init__()
        self.items = items          # list of (name, mesh)
        self.standard = standard

    def run(self):
        for name, mesh in self.items:
            def _cb(frac, msg, _name=name):
                self.progress.emit(frac, f"{_name}: {msg}")

            result = fits_choke_cylinder(
                mesh,
                standard=self.standard,
                name=name,
                progress_callback=_cb,
            )
            self.result_ready.emit(result, mesh)
        self.finished_all.emit()


# ── Main window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choke Test Safety Check")
        self.resize(1100, 600)

        self._standard_key = DEFAULT_STANDARD_KEY
        self._standard = BUILTIN_STANDARDS[self._standard_key]
        self._meshes: dict = {}      # name → mesh  (for preview)
        self._results: List[ChokeResult] = []
        self._worker: Optional[AnalysisWorker] = None

        self.setAcceptDrops(True)

        self._build_ui()
        self._build_menu()
        self._build_statusbar()

    # ── UI construction ──────────────────────────────────────────────────

    def _build_ui(self):
        # Central widget with stacked layout: drop zone (shown when empty)
        # overlaid on the splitter (shown after first analysis)
        from PySide6.QtWidgets import QStackedWidget, QFrame

        self._stack = QStackedWidget()

        # Page 0: drop zone prompt
        drop_frame = QFrame()
        drop_frame.setStyleSheet("""
            QFrame {
                background: #FAFAFA;
                border: 3px dashed #BDBDBD;
                border-radius: 16px;
                margin: 40px;
            }
        """)
        drop_layout = QVBoxLayout(drop_frame)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel("\U0001f4e6")
        icon_label.setStyleSheet("font-size: 64px; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(icon_label)

        hint_label = QLabel(
            "Drag & drop .stl or .3mf files here\n"
            "or use File \u2192 Open"
        )
        hint_label.setStyleSheet(
            "font-size: 16px; color: #757575; border: none;"
        )
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(hint_label)

        self._stack.addWidget(drop_frame)   # index 0

        # Page 1: results splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.table = ResultsTable()
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        splitter.addWidget(self.table)

        self.preview = PreviewWidget()
        splitter.addWidget(self.preview)

        splitter.setSizes([550, 450])
        self._stack.addWidget(splitter)     # index 1

        self._stack.setCurrentIndex(0)      # start on drop zone
        self.setCentralWidget(self._stack)

    def _build_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_stl = file_menu.addAction("Open STL(s)\u2026")
        open_stl.setShortcut("Ctrl+O")
        open_stl.triggered.connect(self.open_stl_files)

        open_3mf = file_menu.addAction("Open Bambu Project (.3mf)\u2026")
        open_3mf.setShortcut("Ctrl+Shift+O")
        open_3mf.triggered.connect(self.open_3mf_project)

        file_menu.addSeparator()

        export_pdf = file_menu.addAction("Export PDF Report\u2026")
        export_pdf.setShortcut("Ctrl+E")
        export_pdf.triggered.connect(self._export_pdf)

        file_menu.addSeparator()

        batch_action = file_menu.addAction("Batch Process Folder\u2026")
        batch_action.triggered.connect(self._batch_process)

        file_menu.addSeparator()

        quit_action = file_menu.addAction("Quit")
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        standard_action = settings_menu.addAction("Choke Standard\u2026")
        standard_action.triggered.connect(self._open_settings)

        clear_cache_action = settings_menu.addAction("Clear Cache")
        clear_cache_action.triggered.connect(clear_cache)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about = help_menu.addAction("About")
        about.triggered.connect(self._show_about)

    def _build_statusbar(self):
        self.statusBar().showMessage("Ready")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)

        self.standard_label = QLabel(self._standard.name)
        self.standard_label.setStyleSheet("padding-right: 8px; color: #555;")
        self.statusBar().addPermanentWidget(self.standard_label)

    # ── Drag and drop ─────────────────────────────────────────────────────

    _SUPPORTED_EXTENSIONS = {".stl", ".3mf"}

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # Accept if at least one file has a supported extension
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    ext = Path(url.toLocalFile()).suffix.lower()
                    if ext in self._SUPPORTED_EXTENSIONS:
                        event.acceptProposedAction()
                        self.statusBar().showMessage(
                            "Drop .stl / .3mf files to analyse\u2026"
                        )
                        return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.statusBar().showMessage("Ready")

    def dropEvent(self, event: QDropEvent):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        stl_paths: List[str] = []
        threemf_paths: List[str] = []

        for url in event.mimeData().urls():
            if not url.isLocalFile():
                continue
            path = url.toLocalFile()
            ext = Path(path).suffix.lower()
            if ext == ".stl":
                stl_paths.append(path)
            elif ext == ".3mf":
                threemf_paths.append(path)

        if not stl_paths and not threemf_paths:
            event.ignore()
            return

        event.acceptProposedAction()

        items = []

        # Load STL files
        for p in stl_paths:
            try:
                mesh = trimesh.load(p)
                items.append((Path(p).stem, mesh))
            except Exception as e:
                QMessageBox.warning(
                    self, "Failed to Load STL",
                    f"Could not load {Path(p).name}:\n{e}",
                )

        # Load 3MF files
        for p in threemf_paths:
            try:
                objs = load_3mf_objects(p)
                for o in objs:
                    label = (
                        f"{Path(p).stem}/{o.name}"
                        if len(threemf_paths) > 1
                        else o.name
                    )
                    items.append((label, o.mesh))
            except Exception as e:
                QMessageBox.warning(
                    self, "Failed to Load 3MF",
                    f"Could not load {Path(p).name}:\n{e}",
                )

        if items:
            self._run_analysis(items)

    # ── File opening ─────────────────────────────────────────────────────

    def open_stl_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open STL Files", "", "STL Files (*.stl)"
        )
        if not paths:
            return
        items = []
        for p in paths:
            name = Path(p).stem
            mesh = trimesh.load(p)
            items.append((name, mesh))
        self._run_analysis(items)

    def open_3mf_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Bambu Studio Project", "",
            "Bambu Studio Project (*.3mf)",
        )
        if not path:
            return
        self._load_3mf(path)

    def open_3mf_direct(self, path: str):
        """Called when launched via file association."""
        self._load_3mf(path)

    def _load_3mf(self, path: str):
        try:
            objs = load_3mf_objects(path)
        except Exception as e:
            QMessageBox.warning(self, "Failed to Load Project", str(e))
            return
        items = [(o.name, o.mesh) for o in objs]
        self._run_analysis(items)

    # ── Analysis ─────────────────────────────────────────────────────────

    def _run_analysis(self, items):
        if self._worker and self._worker.isRunning():
            QMessageBox.information(
                self, "Busy", "An analysis is already running."
            )
            return

        # Switch from drop zone to results view
        self._stack.setCurrentIndex(1)

        self.table.clear_results()
        self.preview.clear_preview()
        self._meshes.clear()
        self._results.clear()

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self._worker = AnalysisWorker(items, self._standard)
        self._worker.progress.connect(self._on_progress)
        self._worker.result_ready.connect(self._on_result)
        self._worker.finished_all.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, fraction: float, message: str):
        self.progress_bar.setValue(int(fraction * 100))
        self.statusBar().showMessage(message)

    def _on_result(self, result: ChokeResult, mesh):
        self.table.add_result(result)
        self._results.append(result)
        self._meshes[result.name] = mesh

    def _on_finished(self):
        self.progress_bar.setVisible(False)
        summary = self.table.get_summary()
        self.statusBar().showMessage(
            f"Done \u2014 {summary['total']} objects: "
            f"{summary['fails']} hazards, {summary['passes']} safe"
        )

    # ── Preview ──────────────────────────────────────────────────────────

    def _on_selection_changed(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self.preview.clear_preview()
            return
        row_idx = rows[0].row()
        if row_idx < len(self._results):
            result = self._results[row_idx]
            mesh = self._meshes.get(result.name)
            self.preview.show_result(result, mesh)

    # ── Settings ─────────────────────────────────────────────────────────

    def _open_settings(self):
        dlg = SettingsDialog(self._standard_key, parent=self)
        if dlg.exec():
            self._standard = dlg.selected_standard()
            self._standard_key = dlg.selected_key()
            self.standard_label.setText(self._standard.name)

    # ── PDF export ───────────────────────────────────────────────────────

    def _export_pdf(self):
        if not self._results:
            QMessageBox.information(
                self, "Nothing to Export",
                "Run an analysis first before exporting a report.",
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", "choke_test_report.pdf",
            "PDF Files (*.pdf)",
        )
        if not path:
            return

        try:
            from reports.pdf_report import generate_report
            generate_report(self._results, path, self._standard)
            QMessageBox.information(
                self, "Report Saved", f"PDF report saved to:\n{path}"
            )
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", str(e))

    # ── Batch processing ─────────────────────────────────────────────────

    def _batch_process(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder for Batch Processing"
        )
        if not folder:
            return

        items = []
        p = Path(folder)

        # Collect STL files
        for stl in p.glob("*.stl"):
            mesh = trimesh.load(str(stl))
            items.append((stl.stem, mesh))

        # Collect 3MF files
        for tmf in p.glob("*.3mf"):
            try:
                objs = load_3mf_objects(str(tmf))
                for o in objs:
                    items.append((f"{tmf.stem}/{o.name}", o.mesh))
            except Exception:
                pass

        if not items:
            QMessageBox.information(
                self, "No Files Found",
                "No .stl or .3mf files found in the selected folder.",
            )
            return

        self._run_analysis(items)

    # ── About ────────────────────────────────────────────────────────────

    def _show_about(self):
        QMessageBox.about(
            self,
            "Choke Test Safety Check",
            "<b>Choke Test Safety Check</b> v1.0<br><br>"
            "Analyses 3D-printed objects against safety-standard "
            "choke-test cylinders to identify potential choking hazards.<br><br>"
            "Supports US CPSC, EU EN-71, and custom standards.<br><br>"
            "Built for use with Bambu Studio.",
        )
