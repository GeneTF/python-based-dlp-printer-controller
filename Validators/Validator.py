from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtCore import pyqtSignal
from Utils.Math import clamp


class IntValidator(QIntValidator):
    fixup_signal = pyqtSignal(int)

    def __init__(self, bottom_in=0, top_in=0, default_in=0):
        super().__init__(bottom_in, top_in)

        self.default = default_in

    def fixup(self, input_in):
        try:
            input_in = int(input_in)
            self.fixup_signal.emit(clamp(input_in, self.bottom(), self.top()))
        except ValueError:
            self.fixup_signal.emit(self.default)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)


class DoubleValidator(QDoubleValidator):
    fixup_signal = pyqtSignal(float)

    def __init__(self, bottom_in=0.0, top_in=0.0, decimals_in=0, default_in=0.0):
        super().__init__(bottom_in, top_in, decimals_in)

        self.default = default_in

    def fixup(self, input_in):
        try:
            input_in = float(input_in)
            self.fixup_signal.emit(clamp(input_in, self.bottom(), self.top()))
        except ValueError:
            self.fixup_signal.emit(self.default)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

