from PyQt6.QtCore import QObject
from enum import Enum
from PyQt6.QtCore import pyqtSignal, pyqtSlot

import PrepareState
from PrintLogic import ControllerStates
from PrintLogic.States import ExposeState, GapState, WashState
from MainWidgets.ExposureScheduleWidget import ExposureScheduleWidgetGUI
from MainWidgets.STLWidget import STLSelectorGUI
from MainWidgets.ConsoleWidget import ConsoleGUI
from MainWidgets.LayerImageWidget import LayerImageGUI
from PrintLogic.ControllerStates import StateControllerState

import time
import numpy as np


class StateControl(QObject):
    finished = pyqtSignal()
    update_ink_number_indicator = pyqtSignal(int, int)
    update_layer_number_indicator = pyqtSignal(int, int)
    update_z_pos_indicator = pyqtSignal(float, float)

    rest_period = 10

    def __init__(self, console_in, schedule_gui_in, stl_selector_in, layer_image_gui_in):
        super().__init__()
        self.console = console_in  # type: ConsoleGUI.Console
        self.schedule_gui = schedule_gui_in  # type: ExposureScheduleWidgetGUI.ExposureScheduleWidget
        self.stl_selector = stl_selector_in  # type: STLSelectorGUI.STLSelector
        self.layer_image_gui = layer_image_gui_in  # type: LayerImageGUI.LayerImageWidget

        self.max_layers = int(self.stl_selector.get_max_layers())
        self.slices = []  # List that will contain bitmap images for exposure

        self.max_ink_number = 1  # Reflects the number of ink regions to print NOT the location

        self.ink_number = 1
        self.layer = 0

        self.slice_frequency = 50  # slices per second

        self.current_z_pos = 0
        self.max_z_pos = 0

        self.stl_selector.set_mesh_lists()  # Creates a list of meshes in stl selector
        self.stl_selector.set_center_vector()  # Defines the translation vector to move STLs to the center

        self.img_width = self.layer_image_gui.img_width
        self.img_height = self.layer_image_gui.img_height

        self.layer_image = np.zeros((self.img_height, self.img_width, 3), np.uint8)

        self.expose = ExposeState.Expose(self.console, self.schedule_gui)

        self.expose.update_state.connect(self.change_state)
        self.expose.update_ink_number.connect(self.update_ink_number)

        self.gap = GapState.Gap()

        self.wash = WashState.Wash()

        self.STATE = StateControllerState.INIT

    def run(self, progress_in):
        match self.STATE:
            case StateControllerState.INIT:
                self.run_init(progress_in)
            case StateControllerState.PREPARE:
                self.run_prepare(progress_in)
            case StateControllerState.EXPOSE:
                self.run_expose(progress_in)
            case StateControllerState.GAP:
                self.run_gap(progress_in)
            case StateControllerState.WASH:
                self.run_wash(progress_in)
            case StateControllerState.CLOSE:
                pass
            case StateControllerState.REST:
                self.run_rest()

    def run_init(self, progress_in):
        progress_in.emit("\n")

        # Groups STLs by their ink number and puts these groups in a list called STL lists
        self.stl_selector.set_stl_lists()

        self.max_ink_number = self.stl_selector.max_ink_number()
        self.expose.max_ink_number = self.max_ink_number
        progress_in.emit("Max ink number: " + str(self.max_ink_number) + "\n")

        progress_in.emit("STL file names and indices:\n")
        for i, stl_list in enumerate(self.stl_selector.stl_lists):
            for j, stl in enumerate(stl_list):
                progress_in.emit(str(i) + " : " + str(j) + " : " + str(stl.file_name.text()) + "\n")

        progress_in.emit("Changing state from DISABLED TO PREPARE.\n")
        self.STATE = StateControllerState.PREPARE

    def run_prepare(self, progress_in):
        exposure_time = self.expose.get_exposure_time(self.layer)
        slice_count = exposure_time * self.slice_frequency
        prepare_state = PrepareState.Prepare()
        self.slices = prepare_state.run(progress_in, self.stl_selector, self.ink_number, self.layer, slice_count,
                                        exposure_time)
        self.STATE = StateControllerState.EXPOSE

    def run_expose(self, progress_in):
        self.update_ink_number_indicator.emit(self.ink_number, self.max_ink_number)
        self.update_layer_number_indicator.emit(self.layer, self.max_layers)
        self.update_z_pos_indicator.emit(self.current_z_pos, self.max_z_pos)
        self.expose.run(progress_in, self.layer, self.slices, self.ink_number, self.max_ink_number, self.slice_frequency)

    def run_gap(self, progress_in):
        self.update_ink_number_indicator.emit(self.ink_number, self.max_ink_number)
        self.update_layer_number_indicator.emit(self.layer, self.max_layers)
        self.update_z_pos_indicator.emit(self.current_z_pos, self.max_z_pos)
        self.gap.run()

    def run_wash(self, progress_in):
        self.update_ink_number_indicator.emit(self.ink_number, self.max_ink_number)
        self.update_layer_number_indicator.emit(self.layer, self.max_layers)
        self.update_z_pos_indicator.emit(self.current_z_pos, self.max_z_pos)
        self.wash.run(progress_in, self.layer, self.ink_number)

    def run_rest(self):
        if self.layer > self.max_layers:
            print("Ending print :)")
            self.STATE = ControllerStates.StateControllerState.CLOSE
            self.finished.emit()
        else:
            print("Setting state to PREPARE after rest")
            time.sleep(self.rest_period)
            self.STATE = ControllerStates.StateControllerState.PREPARE

    def update_ink_number(self):
        print("Updating the ink number")
        self.ink_number += 1

    def update_layer(self):
        self.layer += 1

    def update_z_pos(self, z_pos_in):
        print("Calculating current z position")
        self.current_z_pos = float(z_pos_in) * self.gap.um_per_step * 10**-3

    def reset_ink_number(self):
        self.ink_number = 1

    def change_state(self, state_in):
        self.STATE = state_in
