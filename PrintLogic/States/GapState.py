from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum
import time

from PrintLogic import ControllerStates
import MainConstants


class Gap(QObject):
    move_z_motor = pyqtSignal(float, float, bool)
    finish_moves = pyqtSignal()

    update_z_pos = pyqtSignal()

    update_layer = pyqtSignal()
    change_state = pyqtSignal(object)

    z_up_feedrate = 200

    wait_time = 0.5

    class State(Enum):
        INIT = 0
        GAP = 1

    def __init__(self):
        super().__init__()

        self.STATE = self.State.INIT

        self.layer_height = MainConstants.DEFAULT_LAYER_HEIGHT
        self.um_per_step = MainConstants.DEFAULT_UM_PER_STEP

    def init(self):
        pos_in = self.layer_height / self.um_per_step
        self.move_z_motor.emit(pos_in, self.z_up_feedrate, True)
        self.STATE = self.State.GAP

    def gap(self):
        print("Sending finish moves signal")
        self.finish_moves.emit()
        time.sleep(self.wait_time)

    def close(self):
        print(self.STATE)
        self.STATE = self.State.INIT
        print("Updating z pos")
        self.update_z_pos.emit()
        print("Setting controller state to REST")
        self.change_state.emit(ControllerStates.StateControllerState.REST)
        print("Updating the layer")
        self.update_layer.emit()
        print("Layer updated")

    def run(self):
        match self.STATE:
            case self.State.INIT:
                self.init()
            case self.State.GAP:
                self.gap()
    