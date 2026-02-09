"""
Application entry point — creates the QApplication and shows the main window.
"""

import sys
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from .main_window import MainWindow


def run_app(open_path: Optional[str] = None):
    """
    Launch the Choke Test Safety Check GUI.

    Parameters
    ----------
    open_path : str, optional
        If provided, automatically opens and analyses this .3mf or .stl file.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Choke Test Safety Check")
    app.setOrganizationName("BambuChokeCheck")

    # Apply a clean style
    app.setStyleSheet("""
        QMainWindow { background: #FAFAFA; }
        QTableWidget { font-size: 13px; }
        QMenuBar { background: #EEEEEE; }
        QStatusBar { background: #F5F5F5; font-size: 12px; }
        QProgressBar { text-align: center; }
    """)

    window = MainWindow()

    if open_path:
        if open_path.lower().endswith(".3mf"):
            window.open_3mf_direct(open_path)
        elif open_path.lower().endswith(".stl"):
            import trimesh
            from pathlib import Path
            mesh = trimesh.load(open_path)
            window._run_analysis([(Path(open_path).stem, mesh)])

    window.show()
    sys.exit(app.exec())
