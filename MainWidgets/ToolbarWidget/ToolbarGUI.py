from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QComboBox, QLineEdit
from PyQt6.QtCore import Qt, pyqtSlot, QThread
from MainWidgets.CustomWidgetGUI import CustomWidget
import serial
import serial.tools.list_ports
from MainWidgets.ConsoleWidget import ConsoleGUI
from MainWidgets.MotorControllerWidget import MotorControllerGUI
from MainWidgets.ToolbarWidget.ToolbarFunctionality import ToolbarWorker
from Utils import Messaging


class Toolbar(CustomWidget):
    def __init__(self, console_in, motor_controller_in):
        super().__init__()
        self.console = console_in  # type: ConsoleGUI.Console
        self.motor_controller = motor_controller_in  # type: MotorControllerGUI.MotorController

        self.messenger = Messaging.Messenger(self.console.console_feed)

        self.toolbar_layout = QHBoxLayout()

        self.port = QPushButton()
        self.connect_button = QPushButton()
        self.com_ports = QComboBox()
        self.baudrate = QLineEdit()

        self.set_up_widgets()
        self.set_up_layout()

    def set_up_widgets(self):
        self.port.setText("Port")
        self.connect_button.setText("Connect")
        self.baudrate.setText("115200")

        self.fix_size_policy(self.port)
        self.fix_size_policy(self.connect_button)
        self.fix_size_policy(self.com_ports)
        self.fix_size_policy(self.baudrate)

        self.update_coms()

        self.port.clicked.connect(self.update_coms)

        # Attach command input to send command function
        self.console.command_input.returnPressed.connect(self.write)

    def set_up_layout(self):
        self.toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.toolbar_layout.addWidget(self.port)
        self.toolbar_layout.addWidget(self.connect_button)
        self.toolbar_layout.addWidget(self.com_ports)
        self.toolbar_layout.addWidget(self.baudrate)

        self.setLayout(self.toolbar_layout)

    def update_coms(self):
        self.com_ports.clear()

        # Obtains a list of COMs
        ports = serial.tools.list_ports.comports()

        for port in sorted(ports):
            self.com_ports.addItem(str(port).split(" - ")[0])

    def initialize_worker(self):
        self.thread = QThread()
        self.toolbar_worker = ToolbarWorker()
        self.motor_controller.motor_controller_worker.set_toolbar_worker(self.toolbar_worker)
        self.toolbar_worker.moveToThread(self.thread)

    def get_worker(self):
        return self.toolbar_worker

    def connect(self):
        com = self.com_ports.currentText()
        baudrate = self.baudrate.text()

        self.toolbar_worker.set_values(com, baudrate)

        # Attempt to connect
        try:
            self.thread.started.connect(self.toolbar_worker.connect)
            self.toolbar_worker.finished.connect(self.thread.quit)
            self.toolbar_worker.read_line.connect(self.messenger.update_console)
            self.toolbar_worker.error.connect(self.messenger.generic_error)
            self.toolbar_worker.wrong_serial.connect(self.messenger.error)
            self.toolbar_worker.finished.connect(self.toolbar_worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            # self.toolbar_worker.connected.connect(self.delete_worker)

            self.thread.start()

            self.connect_button.setEnabled(False)

            self.thread.finished.connect(
                lambda: self.connect_button.setEnabled(True)  # Lambda is a function written in one line
            )
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

    @pyqtSlot()
    def write(self):
        try:
            command = self.console.command_input.text() + "\n"
            self.toolbar_worker.flush_input(2)
            self.toolbar_worker.write_command(command.encode("utf-8"))
            message = self.toolbar_worker.read(0)
            current_text = self.console.console_feed.toPlainText()
            current_text += message
            self.console.console_feed.setText(current_text)
        except Exception as ex:
            self.messenger.generic_error(ex)
