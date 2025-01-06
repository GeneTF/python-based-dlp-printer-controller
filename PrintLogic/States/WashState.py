from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum
import MainConstants
import time
from PrintLogic import ControllerStates


class Wash(QObject):
    finish_moves_signal = pyqtSignal()
    write_command = pyqtSignal(str)

    update_ink_number = pyqtSignal()
    reset_ink_number = pyqtSignal()
    update_layer = pyqtSignal()

    update_z_pos = pyqtSignal()

    move_up_feedrate = 1000
    move_down_feedrate = 1000
    move_x_feedrate = 200

    change_state = pyqtSignal(object)

    wait_time = 3

    class State(Enum):
        INIT = 0
        FINISH_MOVES = 1
        CLOSE = 2

    def __init__(self):
        super().__init__()
        self.wash_position = MainConstants.DEFAULT_WASH_POSITION

        self.layer_height = MainConstants.DEFAULT_LAYER_HEIGHT
        self.um_per_step = MainConstants.DEFAULT_UM_PER_STEP
        self.retraction_height = MainConstants.DEFAULT_RETRACTION_HEIGHT
        self.wash_wait_time = MainConstants.DEFAULT_WASH_WAIT
        self.current_x_pos = 0
        self.tray_locations = []

        self.PREV_STATE = None
        self.STATE = self.State.INIT

    def init(self, progress_in, layer_in, ink_number_in):
        print("Got here")

        commands = [f"G0 Z{(self.retraction_height / (self.um_per_step * 10**-3)):.2f} F{self.move_up_feedrate:.2f}",
                    f"G0 X{(self.current_x_pos + self.tray_locations[-1]):.2f} F{self.move_x_feedrate:.2f}",
                    f"G0 Z{((self.wash_position + layer_in * self.layer_height * 10**-3) / (self.um_per_step * 10**-3)):.2f} F{self.move_down_feedrate:.2f}",
                    f"G4 P{self.wash_wait_time * 1000:.2f}",
                    f"G0 Z{(self.retraction_height / (self.um_per_step * 10**-3)):.2f} F{self.move_up_feedrate:.2f}",
                    f"G0 X{(self.current_x_pos + self.tray_locations[ink_number_in-1]):.2f} F{self.move_x_feedrate:.2f}",
                    f"G0 Z{((layer_in * self.layer_height) / self.um_per_step)} F{self.move_down_feedrate:.2f}"]

        command = "\n".join(commands)
        print(command)
        print(ink_number_in)

        self.write_command.emit(command)
        self.PREV_STATE = self.State.INIT
        self.STATE = self.State.FINISH_MOVES

    def finish_moves(self):
        self.finish_moves_signal.emit()
        time.sleep(self.wait_time)

    def close(self):
        self.PREV_STATE = None
        self.STATE = self.State.INIT
        self.update_z_pos.emit()
        self.change_state.emit(ControllerStates.StateControllerState.REST)

    def update(self):
        match self.PREV_STATE:
            case self.State.INIT:
                self.PREV_STATE = self.State.INIT
                self.STATE = self.State.CLOSE

    def run(self, progress_in, layer_in, ink_number_in):
        match self.STATE:
            case self.State.INIT:
                self.init(progress_in, layer_in, ink_number_in)
            case self.State.CLOSE:
                self.close()
            case self.State.FINISH_MOVES:
                self.finish_moves()
