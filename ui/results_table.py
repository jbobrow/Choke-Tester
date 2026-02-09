"""
Results table widget showing choke-test outcomes for each object.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

from analyzer.choke_check import ChokeResult


class ResultsTable(QTableWidget):
    HEADERS = ["Object", "Status", "Diameter (mm)", "Height (mm)", "Standard"]

    # Colours
    COLOR_FAIL = QColor("#B71C1C")
    COLOR_PASS = QColor("#1B5E20")
    COLOR_FAIL_BG = QColor("#FFEBEE")
    COLOR_PASS_BG = QColor("#E8F5E9")

    def __init__(self):
        super().__init__(0, len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setEditTriggers(self.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)

    def clear_results(self):
        self.setRowCount(0)

    def add_result(self, result: ChokeResult):
        """Append one analysis result to the table."""
        row = self.rowCount()
        self.insertRow(row)

        bg = self.COLOR_FAIL_BG if result.fits else self.COLOR_PASS_BG
        fg = self.COLOR_FAIL if result.fits else self.COLOR_PASS

        # Name
        name_item = QTableWidgetItem(result.name)
        name_item.setBackground(bg)
        self.setItem(row, 0, name_item)

        # Status
        status_text = (
            "\u26a0 CHOKING HAZARD" if result.fits else "\u2714 SAFE"
        )
        status_item = QTableWidgetItem(status_text)
        status_item.setForeground(fg)
        status_item.setBackground(bg)
        bold = QFont()
        bold.setBold(True)
        status_item.setFont(bold)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 1, status_item)

        # Diameter
        d_text = f"{result.diameter_mm:.1f}" if result.diameter_mm else "\u2014"
        d_item = QTableWidgetItem(d_text)
        d_item.setBackground(bg)
        d_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 2, d_item)

        # Height
        h_text = f"{result.height_mm:.1f}" if result.height_mm else "\u2014"
        h_item = QTableWidgetItem(h_text)
        h_item.setBackground(bg)
        h_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 3, h_item)

        # Standard
        std_item = QTableWidgetItem(result.standard.name)
        std_item.setBackground(bg)
        self.setItem(row, 4, std_item)

    def get_summary(self) -> dict:
        """Return counts for reporting."""
        total = self.rowCount()
        fails = sum(
            1
            for r in range(total)
            if self.item(r, 1) and "\u26a0" in self.item(r, 1).text()
        )
        return {"total": total, "fails": fails, "passes": total - fails}
