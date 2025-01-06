from PyQt6.QtWidgets import QWidget, QGroupBox, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from MainWidgets.CustomWidgetGUI import CustomWidget
from Validators.Validator import IntValidator, DoubleValidator


class ParameterContainer(CustomWidget):
    def __init__(self, max_param_width_in=50):
        super().__init__()

        self.max_param_width = max_param_width_in
        self.parameter_container_layout = QVBoxLayout()

        self.group = QGroupBox()
        self.group_layout = QVBoxLayout()

        self.set_up_widgets()
        self.set_up_layout()

        self.setEnabled(False)

    def set_up_widgets(self):
        pass

    def add_widget(self, param_name_in, param_in, validator_in=None, editing_finished_seq=None):
        """
        :param func_in:
        :param param_name_in:
        :param param_in:
        :param validator_in:
        :type validator_in: IntValidator | DoubleValidator
        :return:
        """
        widget = ParameterObject()
        widget.set_up_widgets()
        widget.set_up_layout()
        widget.param_name.setText(param_name_in)
        widget.param.setText(str(param_in))
        widget.param.setMaximumWidth(self.max_param_width)
        widget.param.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if validator_in is not None:
            widget.set_validator(validator_in)

        if editing_finished_seq is not None:
            for func in editing_finished_seq:
                widget.param.editingFinished.connect(func)

        self.group_layout.addWidget(widget)
        return widget

    def set_up_layout(self):
        self.parameter_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.group.setLayout(self.group_layout)

        self.parameter_container_layout.addWidget(self.group)

        self.setLayout(self.parameter_container_layout)

    def set_max_param_width(self, width_in):
        self.max_param_width = width_in

    def edit_finish_connect(self, index, func_seq):
        child = self.group.children()[index]

        if isinstance(child, ParameterObject):
            for func in func_seq:
                child.param.editingFinished.connect(func)


class ParameterObject(QWidget):
    def __init__(self):
        super().__init__()

        self.obj_layout = QHBoxLayout()

        self.param_name = QLabel()
        self.param = QLineEdit()

        self.set_up_widgets()
        self.set_up_layout()

    def set_up_widgets(self):
        pass

    def set_up_layout(self):
        self.obj_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.obj_layout.setSpacing(0)
        self.obj_layout.setContentsMargins(0, 0, 0, 0)

        self.obj_layout.addWidget(self.param)
        self.obj_layout.addWidget(self.param_name)

        self.setLayout(self.obj_layout)

    def is_empty(self):
        return self.param.text() == ""

    def set_validator(self, validator_in):
        validator_in.fixup_signal.connect(self.fixup)
        self.param.setValidator(validator_in)

    def fixup(self, input_in):
        self.param.setText(str(input_in))
