from PyQt6.QtWidgets import QWidget, QComboBox, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QStackedLayout
from PyQt6.QtCore import Qt
from MainWidgets.CustomWidgetGUI import CustomWidget
from MainWidgets.ParameterContainerWidget import ParameterContainerGUI
from Validators.Validator import DoubleValidator, IntValidator


class ConstantExposureWidget(CustomWidget):
    def __init__(self):
        super().__init__()

        self.widget_layout = QVBoxLayout()
        self.exposure = ParameterContainerGUI.ParameterObject()

        self.set_up_widgets()
        self.set_up_layout()

    def set_up_widgets(self):
        self.exposure.set_validator(DoubleValidator(1, 600, 2, 15))

        self.exposure.param.setText("5")

        self.exposure.param_name.setText("Exposure Time (s)")

        self.exposure.param.setMaximumWidth(40)

        self.exposure.param.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.fix_size_policy(self.exposure.param_name)

    def set_up_layout(self):
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.widget_layout.addWidget(self.exposure)

        self.setLayout(self.widget_layout)

    def is_empty(self):
        return self.exposure.is_empty()


class WarmupExposureWidget(CustomWidget):
    def __init__(self):
        super().__init__()

        self.widget_layout = QVBoxLayout()

        self.base_exposure = ParameterContainerGUI.ParameterObject()
        self.base_count = ParameterContainerGUI.ParameterObject()

        self.body_exposure = ParameterContainerGUI.ParameterObject()

        self.set_up_widgets()
        self.set_up_layout()

    def set_up_widgets(self):
        self.base_exposure.set_validator(DoubleValidator(1, 600, 2, 30))
        self.base_count.set_validator(IntValidator(1, 1000, 5))

        self.base_exposure.param.setText("10")
        self.base_count.param.setText("5")

        self.base_exposure.param_name.setText("Base Exposure (s)")
        self.base_count.param_name.setText("Number of Base Layers")

        self.body_exposure.set_validator(DoubleValidator(1, 600, 2, 15))
        self.body_exposure.param.setText("5")

        self.body_exposure.param_name.setText("Body Exposure (s)")

        self.base_exposure.param.setMaximumWidth(40)
        self.base_count.param.setMaximumWidth(40)

        self.body_exposure.param.setMaximumWidth(40)

        self.fix_size_policy(self.base_exposure.param_name)
        self.fix_size_policy(self.base_count.param_name)
        self.fix_size_policy(self.body_exposure.param_name)

        self.base_exposure.param.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.base_count.param.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.body_exposure.param.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_up_layout(self):
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.widget_layout.addWidget(self.base_exposure)
        self.widget_layout.addWidget(self.base_count)
        self.widget_layout.addSpacing(10)

        self.widget_layout.addWidget(self.body_exposure)

        self.setLayout(self.widget_layout)

    def is_empty(self):
        conditions = [self.base_exposure.is_empty(), self.base_count.is_empty(), self.body_exposure.is_empty()]
        return any(conditions)


class ExposureScheduleWidget(CustomWidget):
    def __init__(self):
        super().__init__()

        self.stack = QStackedLayout()

        self.label = QLabel()
        self.schedule = QComboBox()
        self.widget_layout = QVBoxLayout()

        self.constant_exposure = ConstantExposureWidget()
        self.warmup_exposure = WarmupExposureWidget()

        self.set_up_widgets()
        self.set_up_layout()

        self.setEnabled(False)

    def set_up_widgets(self):
        self.label.setText("Exposure Schedule")
        self.schedule.addItem("Constant")
        self.schedule.addItem("Warmup")

        self.fix_size_policy(self.label)
        self.fix_size_policy(self.schedule)

        self.stack.addWidget(self.constant_exposure)
        self.stack.addWidget(self.warmup_exposure)

        self.schedule.activated[int].connect(self.stack.setCurrentIndex)

    def set_up_layout(self):
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addWidget(self.schedule)
        self.widget_layout.addLayout(self.stack)

        self.setLayout(self.widget_layout)

    def is_empty(self):
        return self.stack.currentWidget().is_empty()
