"""Input and optimization-bound controls."""

from __future__ import annotations

from PyQt5.QtWidgets import QCheckBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QWidget


FIELD_DEFS = [
    ("coils", "Number of Coils", "12", "6", "72"),
    ("turns", "Number of Turns", "", "1", "200"),
    ("input_voltage", "Input Voltage (V)", "36", "12", "144"),
    ("input_is_vdc", "Voltage Is DC Bus", False, None, None),
    ("modulation_index", "Modulation Index", "0.95", "0.5", "1.0"),
    ("outer_radius", "Outer Radius (m)", "0.127", "0.03", "0.5"),
    ("desired_torque", "Desired Torque (N-m)", "50", "1", "500"),
    ("esc_frequency", "ESC Frequency (Hz)", "", "5", "1000"),
    ("mechanical_rpm", "Mechanical RPM", "750", "50", "12000"),
    ("poles", "Poles", "8", "4", "64"),
    ("winding_factor", "Winding Factor", "0.92", "0.65", "0.98"),
    ("magnetic_flux_density", "Magnetic Flux Density (T)", "0.6", "0.2", "1.4"),
    ("dual_plate", "Dual Plate", False, None, None),
    ("phase_current_limit", "Phase Current Limit (A)", "", "10", "600"),
    ("dc_current_limit", "DC Current Limit (A)", "", "5", "400"),
    ("esc_freq_max", "ESC Freq Max (Hz)", "", "50", "2000"),
]

FLOAT_FIELDS = {"input_voltage", "modulation_index", "outer_radius", "desired_torque", "esc_frequency", "mechanical_rpm", "winding_factor", "magnetic_flux_density", "phase_current_limit", "dc_current_limit", "esc_freq_max"}
INT_FIELDS = {"coils", "turns", "poles"}
BOOL_FIELDS = {"input_is_vdc", "dual_plate"}


class InputPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Inputs and Optimizer Bounds", parent)
        self.value_widgets = {}
        self.optimize_widgets = {}
        self.low_widgets = {}
        self.high_widgets = {}
        layout = QFormLayout(self)

        note = QLabel("Set each variable's fixed value, enable Optimize, then edit Min/Max bounds. Outer Radius bounds are the motor radius search range.")
        note.setWordWrap(True)
        layout.addRow(note)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        for text, width in [("Value", 90), ("Optimize", 75), ("Min", 70), ("Max", 70)]:
            label = QLabel(text)
            label.setMinimumWidth(width)
            header_layout.addWidget(label)
        layout.addRow(QLabel("Variable"), header)

        for name, label, default, low, high in FIELD_DEFS:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            if name in BOOL_FIELDS:
                value = QCheckBox()
                value.setChecked(bool(default))
            else:
                value = QLineEdit(str(default))
                value.setMinimumWidth(90)
            optimize = QCheckBox()
            if name in {"turns", "input_voltage", "outer_radius", "magnetic_flux_density", "poles", "winding_factor", "modulation_index"}:
                optimize.setChecked(True)
            low_edit = QLineEdit("" if low is None else str(low))
            high_edit = QLineEdit("" if high is None else str(high))
            low_edit.setMinimumWidth(70)
            high_edit.setMinimumWidth(70)
            if name == "outer_radius":
                value.setToolTip("Outer radius in meters. Diameter is 2x this value.")
                optimize.setToolTip("Enable to let the optimizer sweep motor outer radius.")
                low_edit.setToolTip("Minimum outer radius in meters for optimization search.")
                high_edit.setToolTip("Maximum outer radius in meters for optimization search.")
            elif name == "input_voltage":
                low_edit.setToolTip("Minimum voltage for architecture sweep. Disable Optimize to fix voltage.")
                high_edit.setToolTip("Maximum voltage for architecture sweep. Disable Optimize to fix voltage.")
            if name in BOOL_FIELDS:
                low_edit.setEnabled(False)
                high_edit.setEnabled(False)
            row_layout.addWidget(value)
            row_layout.addWidget(optimize)
            row_layout.addWidget(low_edit)
            row_layout.addWidget(high_edit)
            self.value_widgets[name] = value
            self.optimize_widgets[name] = optimize
            self.low_widgets[name] = low_edit
            self.high_widgets[name] = high_edit
            display_label = label
            if name == "outer_radius":
                display_label = "Outer Radius Range (m)"
            elif name == "input_voltage":
                display_label = "Input Voltage Range (V)"
            layout.addRow(QLabel(display_label), row)

    def _text_or_none(self, name: str):
        widget = self.value_widgets[name]
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        text = widget.text().strip()
        return None if text == "" else text

    def current_inputs(self) -> dict:
        values = {}
        for name in self.value_widgets:
            raw = self._text_or_none(name)
            if raw is None:
                values[name] = None
            elif name in INT_FIELDS:
                values[name] = int(float(raw))
            elif name in FLOAT_FIELDS:
                values[name] = float(raw)
            elif name in BOOL_FIELDS:
                values[name] = bool(raw)
            else:
                values[name] = raw
        if values.get("mechanical_rpm") is not None:
            values["esc_frequency"] = None
        return values

    def variable_specs(self):
        from axial_motor_calculator.models import VariableSpec

        inputs = self.current_inputs()
        specs = []
        for name, *_ in FIELD_DEFS:
            optimize = self.optimize_widgets[name].isChecked()
            kind = "bool" if name in BOOL_FIELDS else "int" if name in INT_FIELDS else "float"
            low_text = self.low_widgets[name].text().strip()
            high_text = self.high_widgets[name].text().strip()
            low = float(low_text) if low_text else None
            high = float(high_text) if high_text else None
            step = 3 if name == "coils" else 2 if name == "poles" else 1 if name == "turns" else None
            specs.append(VariableSpec(name=name, kind=kind, default=inputs.get(name), optimize=optimize, low=low, high=high, step=step))
        return specs
