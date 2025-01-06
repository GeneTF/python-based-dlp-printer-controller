from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

from MainWidgets.ToolbarWidget import ToolbarFunctionality


class MotorControllerWorker(QObject):
    update_gap_signal = pyqtSignal()
    update_wash_signal = pyqtSignal()

    update_z_pos = pyqtSignal(str)

    ok_counter = 0
    max_ok_counter = 2

    def __init__(self):
        super().__init__()

    def set_toolbar_worker(self, toolbar_worker_in):
        self.toolbar_worker = toolbar_worker_in

    @pyqtSlot()
    def move_x_motor(self, pos_in, feedrate_in, relative=True):
        current_x_pos = self.get_x_pos()

        if relative:
            target_x_pos = float(current_x_pos) + float(pos_in)
        else:
            target_x_pos = float(pos_in)

        command = "G0 X" + str(target_x_pos) + " F" + str(feedrate_in) + "\n"

        self.toolbar_worker.write_command(command.encode("utf-8"))

    @pyqtSlot()
    def move_z_motor(self, pos_in, feedrate_in, relative=True):
        current_z_pos = self.get_z_pos()

        if relative:
            target_z_pos = float(current_z_pos) + float(pos_in)
        else:
            target_z_pos = float(pos_in)

        command = "G0 Z" + str(target_z_pos) + " F" + str(feedrate_in) + "\n"
        self.toolbar_worker.write_command(command.encode("utf-8"))

    @pyqtSlot()
    def finish_moves(self):
        command = "M400\n"
        self.toolbar_worker.write_command(command.encode("utf-8"))

    @pyqtSlot()
    def read(self, count_in):
        return self.toolbar_worker.read(count_in)

    def get_heading(self, flush_input=5, read=2):
        self.toolbar_worker.flush_input(flush_input)
        self.toolbar_worker.write_command("M114\n".encode("utf-8"))
        return self.toolbar_worker.read(read)

    def get_x_pos(self):
        heading = self.get_heading()
        x_pos = heading.split("X:")[1].split("Y:")[0].strip()
        return x_pos

    def get_z_pos(self, heading_in=None, flush_input=5, read=1):
        if heading_in is None:
            heading_in = self.get_heading(flush_input, read)
        z_pos = heading_in.split("Z:")[1].split(" E:")[0].strip()
        return z_pos

    def update(self, count_in):
        self.finish_moves()
        message = self.read(count_in)
        return message

    def update_gap(self):
        message = self.update(1)

        if "ok" in message:
            self.ok_counter += 1

            if self.ok_counter > self.max_ok_counter:
                self.ok_counter = 0
                self.update_gap_signal.emit()

    def update_wash(self):
        self.toolbar_worker: ToolbarFunctionality.ToolbarWorker
        self.toolbar_worker.flush_input(2)

        message = self.update(1)

        if "ok" in message:
            self.ok_counter += 1

            if self.ok_counter > self.max_ok_counter:
                self.ok_counter = 0
                self.update_wash_signal.emit()

    def reset_z_motor(self):
        command = "G92 Z0"
        self.write_command(command)

    def get_current_z(self):
        try:
            print("Getting current z!")
            message: str
            message = self.get_heading(1, 2)
            print(message)
            msg_list = message.split('\n')
            heading = None
            for msg in msg_list:
                if 'X' in msg:
                    heading = msg
            if heading is None:
                self.update_z_pos.emit("-1")
            else:
                self.update_z_pos.emit(self.get_z_pos(heading))
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

    def write_command(self, command_in):
        command = str(command_in) + "\n"
        command = command.encode('utf-8')
        self.toolbar_worker.write_command(command)
