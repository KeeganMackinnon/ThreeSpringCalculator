# ui/main_window.py

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
    QTextEdit,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QScrollArea,
)

from PyQt6.QtGui import QIcon

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from stack import calculate_stack
from plotting import draw_force_curve
from configs import ConfigLibrary
from ui.shock_input_panel import ShockInputPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ANZE Three Spring Calculator")
        self.setWindowIcon(QIcon("assets/anze.ico"))
        self.setMinimumSize(1500, 850)

        self.config_library = ConfigLibrary()

        central_widget = QWidget()
        main_layout = QHBoxLayout()

        left_panel = QWidget()
        left_panel.setMinimumWidth(390)
        left_panel.setMaximumWidth(470)
        left_layout = QVBoxLayout(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # -------------------------
        # Global inputs
        # -------------------------

        self.load_input = self.make_spinbox(0, 5000, 150, " lb", 2)
        self.preload_turns_input = self.make_spinbox(0, 100, 0, " turns", 2)
        self.adjuster_pitch_input = self.make_spinbox(0, 10, 0.0500, " in/turn", 4)
        self.measured_collar_length_input = self.make_spinbox(0, 100, 0, " in", 4)

        global_group = QGroupBox("Global Inputs")
        global_form = QFormLayout()
        global_form.addRow("Applied Load", self.load_input)
        global_form.addRow("Preload Turns", self.preload_turns_input)
        global_form.addRow("Adjuster Thread Pitch", self.adjuster_pitch_input)
        global_form.addRow("Measured Collar Length", self.measured_collar_length_input)
        global_group.setLayout(global_form)

        # -------------------------
        # Config controls
        # -------------------------

        self.config_name_input = QLineEdit()
        self.config_name_input.setPlaceholderText("Config name")

        self.config_select = QComboBox()

        save_config_button = QPushButton("Save Current Config")
        save_config_button.clicked.connect(self.save_current_config)

        load_config_button = QPushButton("Load Selected Config")
        load_config_button.clicked.connect(self.load_selected_config)

        delete_config_button = QPushButton("Delete Selected Config")
        delete_config_button.clicked.connect(self.delete_selected_config)

        config_group = QGroupBox("Spring Configs")
        config_form = QFormLayout()
        config_form.addRow("Name", self.config_name_input)
        config_form.addRow("Saved Configs", self.config_select)
        config_form.addRow(save_config_button)
        config_form.addRow(load_config_button)
        config_form.addRow(delete_config_button)
        config_group.setLayout(config_form)

        # -------------------------
        # Results
        # -------------------------

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        results_layout.addWidget(self.output_box)
        results_group.setLayout(results_layout)

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate)

        left_layout.addWidget(global_group)
        left_layout.addWidget(config_group)
        left_layout.addWidget(results_group, stretch=1)
        left_layout.addWidget(calculate_button)

        # -------------------------
        # Shock input panel
        # -------------------------

        self.shock_input_panel = ShockInputPanel()

        shock_scroll = QScrollArea()
        shock_scroll.setWidgetResizable(True)
        shock_scroll.setWidget(self.shock_input_panel)
        shock_scroll.setMinimumHeight(430)

        shock_group = QGroupBox("Shock Data Input")
        shock_group_layout = QVBoxLayout()
        shock_group_layout.addWidget(shock_scroll)
        shock_group.setLayout(shock_group_layout)

        # -------------------------
        # Plot
        # -------------------------

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        plot_group = QGroupBox("Collar Length vs Force")
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.canvas)
        plot_group.setLayout(plot_layout)

        right_layout.addWidget(shock_group, stretch=3)
        right_layout.addWidget(plot_group, stretch=2)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 4)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.calculate()

    def make_spinbox(self, minimum, maximum, value, suffix="", decimals=2):
        spinbox = QDoubleSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setDecimals(decimals)
        spinbox.setValue(value)
        spinbox.setSuffix(suffix)
        spinbox.setMinimumWidth(140)
        return spinbox

    def get_measured_collar_length(self):
        measured_length = self.measured_collar_length_input.value()

        if measured_length <= 0:
            return None

        return measured_length

    def get_stack(self):
        return self.shock_input_panel.get_stack(
            measured_collar_length=self.get_measured_collar_length()
        )

    def set_stack_inputs(self, stack):
        self.shock_input_panel.set_stack_inputs(stack)

    def refresh_config_dropdown(self):
        current_name = self.config_select.currentText()

        self.config_select.clear()
        self.config_select.addItems(self.config_library.names())

        if current_name:
            index = self.config_select.findText(current_name)
            if index >= 0:
                self.config_select.setCurrentIndex(index)

    def save_current_config(self):
        name = self.config_name_input.text().strip()

        if not name:
            name = f"Config {len(self.config_library.names()) + 1}"

        stack = self.get_stack()
        self.config_library.save_config(name, stack)

        self.refresh_config_dropdown()

        index = self.config_select.findText(name)
        if index >= 0:
            self.config_select.setCurrentIndex(index)

        self.calculate()

    def load_selected_config(self):
        name = self.config_select.currentText()

        if not name:
            return

        stack = self.config_library.load_config(name)
        self.set_stack_inputs(stack)
        self.calculate()

    def delete_selected_config(self):
        name = self.config_select.currentText()

        if not name:
            return

        self.config_library.delete_config(name)
        self.refresh_config_dropdown()
        self.calculate()

    def calculate(self):
        load = self.load_input.value()
        preload_turns = self.preload_turns_input.value()
        adjuster_pitch = self.adjuster_pitch_input.value()

        stack = self.get_stack()

        result = calculate_stack(
            applied_force=load,
            stack=stack,
            preload_turns=preload_turns,
            adjuster_pitch=adjuster_pitch,
        )

        text = ""
        text += f"Applied load: {result.applied_force:.2f} lb\n"
        text += f"Preload turns: {result.preload_turns:.2f}\n"
        text += f"Adjuster pitch: {result.adjuster_pitch:.4f} in/turn\n"
        text += f"Preload displacement: {result.preload_displacement:.4f} in\n"
        text += f"Preload force: {result.preload_force:.2f} lb\n"
        text += f"Total stack force: {result.total_force:.2f} lb\n\n"

        text += f"Total spring compression: {result.total_spring_compression:.4f} in\n"
        text += f"Total spring length: {result.total_spring_length:.4f} in\n"
        text += f"Total coupler length: {result.total_coupler_length:.4f} in\n"
        text += f"Calculated collar length: {result.calculated_collar_length:.4f} in\n"

        if result.measured_collar_length is not None:
            text += f"Measured collar length: {result.measured_collar_length:.4f} in\n"
            text += f"Collar length error: {result.collar_length_error:.4f} in\n"
        else:
            text += "Measured collar length: not entered\n"

        text += "\n"

        for spring_result in result.spring_results:
            text += f"{spring_result.name}\n"
            text += f"  Rate: {spring_result.rate:.2f} lb/in\n"
            text += f"  Free length: {spring_result.free_length:.4f} in\n"

            if spring_result.max_compression is not None:
                text += f"  Calculated max compression: {spring_result.max_compression:.4f} in\n"
            else:
                text += "  Calculated max compression: none\n"

            text += f"  Actual compression: {spring_result.compression:.4f} in\n"
            text += f"  Compressed length: {spring_result.compressed_length:.4f} in\n"
            text += f"  Stopped: {spring_result.stopped}\n\n"

        self.output_box.setText(text)

        draw_force_curve(
            figure=self.figure,
            canvas=self.canvas,
            stack=stack,
            selected_load=load,
            preload_turns=preload_turns,
            adjuster_pitch=adjuster_pitch,
            comparison_stacks=self.config_library.all_configs(),
        )