from PyQt6.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QSpacerItem
from PyQt6.QtCore import Qt, pyqtSignal
from MainWidgets.MotorControllerWidget.MotorControllerFunctionality import MotorControllerWorker
from MainWidgets.CustomWidgetGUI import CustomWidget
from Validators.Validator import IntValidator


class MotorController(CustomWidget):
    def __init__(self, console_in):
        super().__init__()

        self.motor_controller_layout = QVBoxLayout()

        self.console = console_in

        self.motor_controller_worker = MotorControllerWorker()

        self.x_motor_id = QLabel()
        self.z_motor_id = QLabel()

        self.x_motor_speed = QLineEdit()
        self.z_motor_speed = QLineEdit()

        self.x_motor_speed_id = QLabel()
        self.z_motor_speed_id = QLabel()

        self.x_motor_speed_units = QLabel()
        self.z_motor_speed_units = QLabel()

        self.x_moves = [QPushButton() for i in range(10)]
        self.z_moves = [QPushButton() for i in range(10)]

        self.set_up_widgets()
        self.set_up_layout()

        self.setEnabled(False)

    def set_up_widgets(self):
        x_motor_validator = IntValidator(300, 500, 300)
        x_motor_validator.fixup_signal.connect(
            lambda input_in: self.x_motor_speed.setText(str(input_in))
        )
        self.x_motor_speed.setValidator(x_motor_validator)

        z_motor_validator = IntValidator(10, 2000, 1000)
        z_motor_validator.fixup_signal.connect(
            lambda input_in: self.z_motor_speed.setText(str(input_in))
        )
        self.z_motor_speed.setValidator(z_motor_validator)

        self.x_motor_id.setText("X:")
        self.fix_size_policy(self.x_motor_id)

        self.z_motor_id.setText("Z:")
        self.fix_size_policy(self.z_motor_id)

        self.x_motor_speed_id.setText("X:")
        self.fix_size_policy(self.x_motor_speed_id)

        self.x_motor_speed_units.setText("units/s")
        self.fix_size_policy(self.x_motor_speed_units)

        self.z_motor_speed_id.setText("Z:")
        self.fix_size_policy(self.z_motor_speed_id)

        self.z_motor_speed_units.setText("units/s")
        self.fix_size_policy(self.z_motor_speed_units)

        self.x_motor_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.x_motor_speed.setText('300')
        self.x_motor_speed.setMaximumWidth(50)

        self.z_motor_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.z_motor_speed.setText('1000')
        self.z_motor_speed.setMaximumWidth(50)

        # Set up x move buttons
        x_move_vals = [-100, -10, -1, -0.1, -0.01, 0.01, 0.1, 1, 10, 100]

        for i, x_move in enumerate(self.x_moves):
            x_move.setText(str(x_move_vals[i]))
            x_move.clicked.connect(self.move_x_motor)
            x_move.setMaximumWidth(50)

        # Set up z move buttons
        z_move_vals = x_move_vals

        for i, z_move in enumerate(self.z_moves):
            z_move.setText(str(z_move_vals[i]))
            z_move.clicked.connect(self.move_z_motor)
            z_move.setMaximumWidth(50)

    def set_up_layout(self):
        layouts = [QHBoxLayout() for i in range(3)]

        layouts[0].addWidget(self.x_motor_speed_id)
        layouts[0].addWidget(self.x_motor_speed)
        layouts[0].addWidget(self.x_motor_speed_units)
        layouts[0].addSpacing(10)
        layouts[0].addWidget(self.z_motor_speed_id)
        layouts[0].addWidget(self.z_motor_speed)
        layouts[0].addWidget(self.z_motor_speed_units)

        layouts[1].addWidget(self.x_motor_id)
        for x_move in self.x_moves:
            layouts[1].addWidget(x_move)

        layouts[2].addWidget(self.z_motor_id)
        for z_move in self.z_moves:
            layouts[2].addWidget(z_move)

        for layout in layouts:
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.motor_controller_layout.addLayout(layout)

        self.setLayout(self.motor_controller_layout)

    def move_x_motor(self):
        self.motor_controller_worker.move_x_motor(self.sender().text(), self.x_motor_speed.text())

    def move_z_motor(self):
        self.motor_controller_worker.move_z_motor(self.sender().text(), self.z_motor_speed.text())

