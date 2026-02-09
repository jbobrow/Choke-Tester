"""
Settings dialog for choosing / customising the choke-test standard.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QDialogButtonBox,
    QFormLayout,
)
from PySide6.QtCore import Signal

from analyzer.standards import (
    BUILTIN_STANDARDS,
    ChokeStandard,
    custom_standard,
    DEFAULT_STANDARD_KEY,
)


class SettingsDialog(QDialog):
    """Let the user pick a standard or define custom cylinder dimensions."""

    standard_changed = Signal(object)  # emits a ChokeStandard

    def __init__(self, current_key: str = DEFAULT_STANDARD_KEY, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choke Test Settings")
        self.setMinimumWidth(400)

        self._current_key = current_key
        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Standard selector
        selector_group = QGroupBox("Safety Standard")
        sel_layout = QFormLayout(selector_group)

        self.combo = QComboBox()
        for key, std in BUILTIN_STANDARDS.items():
            self.combo.addItem(std.name, userData=key)
        self.combo.addItem("Custom…", userData="custom")
        self.combo.currentIndexChanged.connect(self._on_combo_changed)
        sel_layout.addRow("Standard:", self.combo)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        sel_layout.addRow(self.desc_label)

        layout.addWidget(selector_group)

        # Custom dimensions
        self.custom_group = QGroupBox("Custom Dimensions")
        custom_layout = QFormLayout(self.custom_group)

        self.diameter_spin = QDoubleSpinBox()
        self.diameter_spin.setRange(1.0, 500.0)
        self.diameter_spin.setSuffix(" mm")
        self.diameter_spin.setDecimals(1)
        self.diameter_spin.setValue(31.7)
        custom_layout.addRow("Diameter:", self.diameter_spin)

        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1.0, 500.0)
        self.height_spin.setSuffix(" mm")
        self.height_spin.setDecimals(1)
        self.height_spin.setValue(57.1)
        custom_layout.addRow("Height:", self.height_spin)

        self.custom_group.setVisible(False)
        layout.addWidget(self.custom_group)

        # Dimension preview
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("color: #555; font-style: italic;")
        layout.addWidget(self.preview_label)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Set initial selection
        for i in range(self.combo.count()):
            if self.combo.itemData(i) == self._current_key:
                self.combo.setCurrentIndex(i)
                break
        self._on_combo_changed()

    # ── Slots ────────────────────────────────────────────────────────────

    def _on_combo_changed(self):
        key = self.combo.currentData()
        is_custom = key == "custom"
        self.custom_group.setVisible(is_custom)

        if not is_custom and key in BUILTIN_STANDARDS:
            std = BUILTIN_STANDARDS[key]
            self.desc_label.setText(std.description)
            self.preview_label.setText(
                f"Cylinder: \u00d8{std.diameter_mm} mm \u00d7 {std.height_mm} mm"
            )
        else:
            self.desc_label.setText("Enter your own cylinder dimensions below.")
            self._update_custom_preview()
            self.diameter_spin.valueChanged.connect(self._update_custom_preview)
            self.height_spin.valueChanged.connect(self._update_custom_preview)

    def _update_custom_preview(self):
        d = self.diameter_spin.value()
        h = self.height_spin.value()
        self.preview_label.setText(f"Cylinder: \u00d8{d:.1f} mm \u00d7 {h:.1f} mm")

    # ── Public API ───────────────────────────────────────────────────────

    def selected_standard(self) -> ChokeStandard:
        key = self.combo.currentData()
        if key == "custom":
            return custom_standard(
                name="Custom",
                diameter_mm=self.diameter_spin.value(),
                height_mm=self.height_spin.value(),
            )
        return BUILTIN_STANDARDS[key]

    def selected_key(self) -> str:
        return self.combo.currentData()
