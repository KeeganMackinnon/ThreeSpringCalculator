from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
    QTextEdit,
)
from PyQt6.QtGui import QIcon


from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from plotting import generate_force_curve
from spring import Spring
from stack import basic_stack_calculation


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ANZE Three Spring Calculator")
        self.setWindowIcon(QIcon("assets/anze.ico"))
        self.setMinimumSize(1100, 700)
        
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        input_layout = QVBoxLayout()
        output_layout = QVBoxLayout()

        self.load_input = QDoubleSpinBox()
        self.load_input.setRange(0, 5000)
        self.load_input.setValue(150)
        self.load_input.setSuffix(" lb")

        self.preload_turns_input = QDoubleSpinBox()
        self.preload_turns_input.setRange(0, 100)
        self.preload_turns_input.setDecimals(2)
        self.preload_turns_input.setValue(0)
        self.preload_turns_input.setSuffix(" turns")

        self.adjuster_pitch_input = QDoubleSpinBox()
        self.adjuster_pitch_input.setRange(0, 10)
        self.adjuster_pitch_input.setDecimals(4)
        self.adjuster_pitch_input.setValue(0.050)
        self.adjuster_pitch_input.setSuffix(" in/turn")
        
        self.k1_input = QDoubleSpinBox()
        self.k1_input.setRange(1, 5000)
        self.k1_input.setValue(100)
        self.k1_input.setSuffix(" lb/in")

        self.l1_input = QDoubleSpinBox()
        self.l1_input.setRange(0, 100)
        self.l1_input.setValue(2.0)
        self.l1_input.setSuffix(" in")

        self.stop1_input = QDoubleSpinBox()
        self.stop1_input.setRange(0, 100)
        self.stop1_input.setValue(0.75)
        self.stop1_input.setSuffix(" in")

        self.k2_input = QDoubleSpinBox()
        self.k2_input.setRange(1, 5000)
        self.k2_input.setValue(200)
        self.k2_input.setSuffix(" lb/in")

        self.l2_input = QDoubleSpinBox()
        self.l2_input.setRange(0, 100)
        self.l2_input.setValue(2.5)
        self.l2_input.setSuffix(" in")

        self.stop2_input = QDoubleSpinBox()
        self.stop2_input.setRange(0, 100)
        self.stop2_input.setValue(1.0)
        self.stop2_input.setSuffix(" in")

        self.k3_input = QDoubleSpinBox()
        self.k3_input.setRange(1, 5000)
        self.k3_input.setValue(400)
        self.k3_input.setSuffix(" lb/in")

        self.l3_input = QDoubleSpinBox()
        self.l3_input.setRange(0, 100)
        self.l3_input.setValue(6.0)
        self.l3_input.setSuffix(" in")

        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate)

        input_layout.addWidget(QLabel("Applied Load"))
        input_layout.addWidget(self.load_input)

        input_layout.addWidget(QLabel("Preload Turns"))
        input_layout.addWidget(self.preload_turns_input)

        input_layout.addWidget(QLabel("Adjuster Thread Pitch"))
        input_layout.addWidget(self.adjuster_pitch_input)

        input_layout.addWidget(QLabel("Spring 1 Rate"))
        input_layout.addWidget(self.k1_input)
        input_layout.addWidget(QLabel("Spring 1 Free Length"))
        input_layout.addWidget(self.l1_input)
        input_layout.addWidget(QLabel("Spring 1 Max Compression / Stop"))
        input_layout.addWidget(self.stop1_input)

        input_layout.addWidget(QLabel("Spring 2 Rate"))
        input_layout.addWidget(self.k2_input)
        input_layout.addWidget(QLabel("Spring 2 Free Length"))
        input_layout.addWidget(self.l2_input)
        input_layout.addWidget(QLabel("Spring 2 Max Compression / Stop"))
        input_layout.addWidget(self.stop2_input)

        input_layout.addWidget(QLabel("Main Spring Rate"))
        input_layout.addWidget(self.k3_input)
        input_layout.addWidget(QLabel("Main Spring Free Length"))
        input_layout.addWidget(self.l3_input)

        input_layout.addWidget(calculate_button)
        input_layout.addStretch()

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        # Matplotlib figure embedded into PyQt
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        output_layout.addWidget(QLabel("Results"))
        output_layout.addWidget(self.output_box)
        output_layout.addWidget(QLabel("Force vs Compression"))
        output_layout.addWidget(self.canvas)

        main_layout.addLayout(input_layout, 1)
        main_layout.addLayout(output_layout, 3)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Draw initial result on startup
        self.calculate()

    def get_springs(self):
        return [
            Spring(
                name="Spring 1",
                rate=self.k1_input.value(),
                free_length=self.l1_input.value(),
                max_compression=self.stop1_input.value(),
            ),
            Spring(
                name="Spring 2",
                rate=self.k2_input.value(),
                free_length=self.l2_input.value(),
                max_compression=self.stop2_input.value(),
            ),
            Spring(
                name="Main Spring",
                rate=self.k3_input.value(),
                free_length=self.l3_input.value(),
                max_compression=None,
            ),
        ]

    def calculate(self):
        load = self.load_input.value()
        springs = self.get_springs()

        preload_turns = self.preload_turns_input.value()
        adjuster_pitch = self.adjuster_pitch_input.value()

        result = basic_stack_calculation(
            force=load,
            springs=springs,
            preload_turns=preload_turns,
            adjuster_pitch=adjuster_pitch
)

        text = ""
        text += f"Applied load: {result['applied_force']:.2f} lb\n"
        text += f"Preload turns: {result['preload_turns']:.2f}\n"
        text += f"Adjuster pitch: {result['adjuster_pitch']:.4f} in/turn\n"
        text += f"Preload displacement: {result['preload_displacement']:.3f} in\n"
        text += f"Preload force: {result['preload_force']:.2f} lb\n"
        text += f"Total stack force: {result['total_force']:.2f} lb\n"
        text += f"Total compression: {result['total_compression']:.3f} in\n"
        text += f"Total stack length: {result['total_length']:.3f} in\n\n"

        for spring in result["spring_results"]:
            text += f"{spring['name']}\n"
            text += f"  Compression: {spring['compression']:.3f} in\n"
            text += f"  Compressed length: {spring['compressed_length']:.3f} in\n"
            text += f"  Stopped: {spring['stopped']}\n\n"

        self.output_box.setText(text)
        curve = generate_force_curve(
            springs=springs,
            max_force=max(load * 1.5, 500),
            step=max(load * 1.5, 500) / 100,
            preload_turns=preload_turns,
            adjuster_pitch=adjuster_pitch
        )

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.plot(curve["stack_lengths"], curve["forces"], linewidth=2)

        selected_stack_length = result["total_length"]

        ax.scatter([selected_stack_length], [load], s=60)
        ax.annotate(
            f"{load:.1f} lb\n{selected_stack_length:.2f} in",
            xy=(selected_stack_length, load),
            xytext=(10, 10),
            textcoords="offset points",
        )

        ax.set_xlabel("Compressed Stack Length [in]")
        ax.set_ylabel("Applied Force [lb]")
        ax.set_title("Spring Stack Length vs Force")
        ax.grid(True)
        ax.invert_xaxis()

        self.canvas.draw()