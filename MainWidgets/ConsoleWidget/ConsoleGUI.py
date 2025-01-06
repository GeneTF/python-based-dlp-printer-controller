from PyQt6.QtWidgets import QTextEdit, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt
from MainWidgets.CustomWidgetGUI import CustomWidget
from MainWidgets.LayerIndicatorWidget import LayerIndicatorGUI


class Console(CustomWidget):
    def __init__(self):
        super().__init__()
        self.console_layout = QVBoxLayout()

        self.console_feed = QTextEdit()
        self.console_feed.setReadOnly(True)

        self.command_input = QLineEdit()

        self.layer_indicator = LayerIndicatorGUI.LayerIndicator()

        self.set_up_widgets()
        self.set_up_layout()

        self.setEnabled(False)

    def set_up_widgets(self):
        pass

    def set_up_layout(self):
        self.console_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.console_layout.addWidget(self.layer_indicator)
        self.console_layout.addWidget(self.console_feed)
        self.console_layout.addWidget(self.command_input)

        self.setLayout(self.console_layout)
