from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QDoubleSpinBox,
    QGroupBox,
    QFormLayout,
    QGridLayout,
    QVBoxLayout,
    QFrame,
)

from models import Spring, StopPuck, BlankCoupler, SpringStack


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHOCK_IMAGE_PATH = PROJECT_ROOT / "assets" / "shock_diagram.png"


class ShockInputPanel(QWidget):
    """
    Diagram-style input panel.

    User-facing physical naming:
        Spring 3 = Top Spring
        Spring 2 = Main Spring
        Spring 1 = Bottom Spring

    Internal model mapping:
        spring_1 = Bottom Spring
        spring_2 = Main Spring
        spring_3 = Top Spring
    """

    def __init__(self):
        super().__init__()

        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        main_layout.setColumnStretch(2, 1)

        # -------------------------
        # Shock image / center panel
        # -------------------------

        image_frame = QFrame()
        image_frame.setFrameShape(QFrame.Shape.StyledPanel)

        image_layout = QVBoxLayout(image_frame)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if SHOCK_IMAGE_PATH.exists():
            pixmap = QPixmap(str(SHOCK_IMAGE_PATH))
            self.image_label.setPixmap(
                pixmap.scaled(
                    420,
                    680,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.image_label.setText(
                "Shock Diagram\n\n"
                "Place image here:\n"
                "assets/shock_diagram.png"
            )
            self.image_label.setMinimumSize(420, 680)
            self.image_label.setStyleSheet(
                "border: 1px dashed gray; font-size: 18px;"
            )

        image_layout.addWidget(self.image_label)

        # -------------------------
        # Input groups
        # -------------------------

        self.top_spring_group = self.create_top_spring_group()
        self.main_spring_group = self.create_main_spring_group()
        self.bottom_spring_group = self.create_bottom_spring_group()

        self.puck1_group = self.create_puck1_group()
        self.puck2_group = self.create_puck2_group()

        self.coupler1_group = self.create_coupler1_group()
        self.coupler2_group = self.create_coupler2_group()

        # -------------------------
        # Layout around image
        # -------------------------

        main_layout.addWidget(self.top_spring_group, 0, 2)
        main_layout.addWidget(self.puck2_group, 1, 2)
        main_layout.addWidget(self.coupler2_group, 2, 2)

        main_layout.addWidget(image_frame, 0, 1, 7, 1)

        main_layout.addWidget(self.main_spring_group, 2, 0)
        main_layout.addWidget(self.puck1_group, 3, 0)
        main_layout.addWidget(self.coupler1_group, 4, 2)
        main_layout.addWidget(self.bottom_spring_group, 5, 2)

        self.setLayout(main_layout)

    def make_spinbox(self, minimum, maximum, value, suffix="", decimals=4):
        spinbox = QDoubleSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setDecimals(decimals)
        spinbox.setValue(value)
        spinbox.setSuffix(suffix)
        spinbox.setMinimumWidth(140)
        return spinbox

    def create_top_spring_group(self):
        self.k_top_input = self.make_spinbox(1, 5000, 300, " lb/in", 2)
        self.l_top_input = self.make_spinbox(0, 100, 2.0, " in", 4)

        group = QGroupBox("→ Spring 3")
        form = QFormLayout()
        form.addRow("Rate", self.k_top_input)
        form.addRow("Free Length", self.l_top_input)
        group.setLayout(form)

        return group

    def create_main_spring_group(self):
        self.k_main_input = self.make_spinbox(1, 5000, 200, " lb/in", 2)
        self.l_main_input = self.make_spinbox(0, 100, 2.5, " in", 4)

        group = QGroupBox("Spring 2 ←")
        form = QFormLayout()
        form.addRow("Rate", self.k_main_input)
        form.addRow("Free Length", self.l_main_input)
        group.setLayout(form)

        return group

    def create_bottom_spring_group(self):
        self.k_bottom_input = self.make_spinbox(1, 5000, 100, " lb/in", 2)
        self.l_bottom_input = self.make_spinbox(0, 100, 2.0, " in", 4)

        group = QGroupBox("→ Spring 1 / (Main Spring)")
        form = QFormLayout()
        form.addRow("Rate", self.k_bottom_input)
        form.addRow("Free Length", self.l_bottom_input)
        group.setLayout(form)

        return group

    def create_puck1_group(self):
        self.puck1_thickness_input = self.make_spinbox(0, 100, 0.5, " in", 4)
        self.puck1_top_offset_input = self.make_spinbox(0, 100, 0.0, " in", 4)
        self.puck1_bottom_offset_input = self.make_spinbox(0, 100, 0.0, " in", 4)

        group = QGroupBox("Stop Puck 1 ←")
        form = QFormLayout()
        form.addRow("Thickness", self.puck1_thickness_input)
        form.addRow("Top Offset", self.puck1_top_offset_input)
        form.addRow("Bottom Offset", self.puck1_bottom_offset_input)
        group.setLayout(form)

        return group

    def create_puck2_group(self):
        self.puck2_thickness_input = self.make_spinbox(0, 100, 0.5, " in", 4)
        self.puck2_top_offset_input = self.make_spinbox(0, 100, 0.0, " in", 4)
        self.puck2_bottom_offset_input = self.make_spinbox(0, 100, 0.0, " in", 4)

        group = QGroupBox("→ Stop Puck 2")
        form = QFormLayout()
        form.addRow("Thickness", self.puck2_thickness_input)
        form.addRow("Top Offset", self.puck2_top_offset_input)
        form.addRow("Bottom Offset", self.puck2_bottom_offset_input)
        group.setLayout(form)

        return group

    def create_coupler1_group(self):
        self.coupler1_length_input = self.make_spinbox(0, 100, 0.5, " in", 4)

        group = QGroupBox("→ Blank Coupler 1")
        form = QFormLayout()
        form.addRow("Length", self.coupler1_length_input)
        group.setLayout(form)

        return group

    def create_coupler2_group(self):
        self.coupler2_length_input = self.make_spinbox(0, 100, 0.5, " in", 4)

        group = QGroupBox("Blank Coupler 2 →")
        form = QFormLayout()
        form.addRow("Length", self.coupler2_length_input)
        group.setLayout(form)

        return group

    def get_stack(self, measured_collar_length=None):
        puck_1 = StopPuck(
            thickness=self.puck1_thickness_input.value(),
            top_offset=self.puck1_top_offset_input.value(),
            bottom_offset=self.puck1_bottom_offset_input.value(),
        )

        puck_2 = StopPuck(
            thickness=self.puck2_thickness_input.value(),
            top_offset=self.puck2_top_offset_input.value(),
            bottom_offset=self.puck2_bottom_offset_input.value(),
        )

        bottom_spring = Spring(
            name="Spring 1",
            rate=self.k_bottom_input.value(),
            free_length=self.l_bottom_input.value(),
            stop_puck=puck_1,
        )

        main_spring = Spring(
            name="Spring 2",
            rate=self.k_main_input.value(),
            free_length=self.l_main_input.value(),
            stop_puck=puck_2,
        )

        top_spring = Spring(
            name="Spring 3 (Main Spring)",
            rate=self.k_top_input.value(),
            free_length=self.l_top_input.value(),
            stop_puck=None,
        )

        coupler_1 = BlankCoupler(
            name="Blank Coupler 1",
            length=self.coupler1_length_input.value(),
        )

        coupler_2 = BlankCoupler(
            name="Blank Coupler 2",
            length=self.coupler2_length_input.value(),
        )

        return SpringStack(
            spring_1=bottom_spring,
            coupler_1=coupler_1,
            spring_2=main_spring,
            coupler_2=coupler_2,
            spring_3=top_spring,
            measured_collar_length=measured_collar_length,
        )

    def set_stack_inputs(self, stack):
        # Bottom spring / spring 1
        self.k_bottom_input.setValue(stack.spring_1.rate)
        self.l_bottom_input.setValue(stack.spring_1.free_length)

        if stack.spring_1.stop_puck is not None:
            self.puck1_thickness_input.setValue(stack.spring_1.stop_puck.thickness)
            self.puck1_top_offset_input.setValue(stack.spring_1.stop_puck.top_offset)
            self.puck1_bottom_offset_input.setValue(stack.spring_1.stop_puck.bottom_offset)

        self.coupler1_length_input.setValue(stack.coupler_1.length)

        # Main spring / spring 2
        self.k_main_input.setValue(stack.spring_2.rate)
        self.l_main_input.setValue(stack.spring_2.free_length)

        if stack.spring_2.stop_puck is not None:
            self.puck2_thickness_input.setValue(stack.spring_2.stop_puck.thickness)
            self.puck2_top_offset_input.setValue(stack.spring_2.stop_puck.top_offset)
            self.puck2_bottom_offset_input.setValue(stack.spring_2.stop_puck.bottom_offset)

        self.coupler2_length_input.setValue(stack.coupler_2.length)

        # Top spring / spring 3
        self.k_top_input.setValue(stack.spring_3.rate)
        self.l_top_input.setValue(stack.spring_3.free_length)