from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
import serial


class ToolbarWorker(QObject):
    finished = pyqtSignal()
    connected = pyqtSignal(bool)
    read_line = pyqtSignal(str)
    wrong_serial = pyqtSignal(str)
    error = pyqtSignal(Exception)

    def __init__(self, port_in='COM3', baudrate_in=115200, timeout_in=1000):
        super().__init__()

        self.ser = serial.Serial()
        self.port = port_in
        self.baudrate = baudrate_in
        self.timeout = timeout_in

    def set_values(self, port_in, baudrate_in):
        self.port = port_in
        self.baudrate = baudrate_in

    @pyqtSlot()
    def connect(self):
        try:
            self.ser.port = self.port
            self.ser.baudrate = self.baudrate
            self.ser.timeout = self.timeout
            self.ser.open()
            self.ser.write(b'G0 Z0\n')
            self.ser.flushInput()
            self.ser.flushOutput()
            self.connected.emit(True)
        except serial.SerialException:
            self.connected.emit(False)
            self.wrong_serial.emit("Unable to connect to printer! Try a different COM.")
        except Exception as ex:
            self.connected.emit(False)
            self.error.emit(ex)

        self.finished.emit()

    @pyqtSlot()
    def read_startup(self):
        """
        Attempting to read line from DLP printer.
        A generic line will return a bytes type object.
        It can be decoded using "utf-8"
        Reading for constant number of times for now rather than checking at what point to stop.
        """
        for i in range(7):
            self.read_line.emit(self.ser.read_until().decode('utf-8'))

    def write_command(self, command_in):
        self.ser.write(command_in)

    def flush_input(self, count_in=1):
        for i in range(count_in):
            self.ser.flushInput()

    def read(self, count_in=1):
        message = ""
        for i in range(count_in):
            try:
                message += self.ser.read_until(b'\n').decode("utf-8")
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)

        return message
