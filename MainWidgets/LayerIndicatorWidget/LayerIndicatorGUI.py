from PyQt6.QtWidgets import QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from MainWidgets.CustomWidgetGUI import CustomWidget


class Indicator(CustomWidget):
    def __init__(self):
        super().__init__()
        self.widget_layout = QHBoxLayout()

        self.indicator = QLabel()
        self.indicator_name = QLabel()

        self.reset_indicator()

        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.widget_layout.setSpacing(0)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)

        self.widget_layout.addWidget(self.indicator_name)
        self.widget_layout.addWidget(self.indicator)

        self.setLayout(self.widget_layout)

    def update_indicator(self, param_one_in, param_two_in):
        self.indicator.setText(str(param_one_in) + "/" + str(param_two_in))

    def reset_indicator(self):
        self.update_indicator("-", "-")


class LayerIndicator(CustomWidget):
    def __init__(self):
        super().__init__()

        self.widget_layout = QHBoxLayout()

        self.ink_number = Indicator()
        self.ink_number.indicator_name.setText("Ink Number:")

        self.layer_number = Indicator()
        self.layer_number.indicator_name.setText("Layer Number:")

        self.exposure_time = Indicator()
        self.exposure_time.indicator_name.setText("Exposure Time:")

        self.z_motor_position = Indicator()
        self.z_motor_position.indicator_name.setText("Z Pos:")

        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.widget_layout.setSpacing(0)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)

        self.widget_layout.addWidget(self.layer_number)
        self.widget_layout.addStretch()
        self.widget_layout.addWidget(self.z_motor_position)
        self.widget_layout.addStretch()
        self.widget_layout.addWidget(self.ink_number)
        self.widget_layout.addStretch()
        self.widget_layout.addWidget(self.exposure_time)

        self.setLayout(self.widget_layout)
