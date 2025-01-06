import time

from PyQt6.QtCore import QObject, pyqtSignal
from MainWidgets.ExposureScheduleWidget import ExposureScheduleWidgetGUI
from MainWidgets.ConsoleWidget import ConsoleGUI
from PrintLogic.ControllerStates import StateControllerState
from enum import Enum
import numpy as np


class Expose(QObject):
    update_state = pyqtSignal(object)
    update_ink_number = pyqtSignal()
    reset_ink_number = pyqtSignal()
    update_layer = pyqtSignal()
    update_exposure_time_indicator = pyqtSignal(float, float)
    update_layer_image = pyqtSignal(object)
    reset_layer_image = pyqtSignal()

    time_to_update_indicators = 5

    class State(Enum):
        INIT = 0
        EXPOSE = 1

    def __init__(self, console_in, schedule_gui_in):
        super().__init__()
        self.console = console_in  # type: ConsoleGUI.Console

        self.schedule_gui = schedule_gui_in  # type: ExposureScheduleWidgetGUI.ExposureScheduleWidget
        self.schedule = self.schedule_gui.schedule
        self.schedule_name = self.schedule.currentText()

        self.stack = self.schedule_gui.stack

        self.start_time = 0
        self.delta_time = 0

        self.STATE = self.State.INIT

    def get_exposure_time(self, layer_in):
        if self.schedule_name == "Constant":
            current_widget = self.stack.currentWidget()  # type: ExposureScheduleWidgetGUI.ConstantExposureWidget
            exposure_time = float(current_widget.exposure.param.text())
            return exposure_time

        elif self.schedule_name == "Warmup":
            current_widget = self.stack.currentWidget()  # type: ExposureScheduleWidgetGUI.WarmupExposureWidget
            base_exposure_time = float(current_widget.base_exposure.param.text())
            base_layer_count = float(current_widget.base_count.param.text())

            body_exposure_time = float(current_widget.body_exposure.param.text())

            # If the current layer is still within the base layers
            if layer_in < base_layer_count:
                return base_exposure_time

            # Otherwise it is in the body count range
            else:
                return body_exposure_time

    def init(self, progress_in, layer_in, layer_image_in):
        self.start_time = time.time()
        print("Setting expose state to EXPOSE")
        self.STATE = self.State.EXPOSE

    def expose(self, progress_in, layer_in, slices_in, ink_number_in, max_ink_number_in, slice_frequency_in):
        self.delta_time = time.time() - self.start_time

        slice_index = int(self.delta_time * slice_frequency_in)

        if slice_index >= len(slices_in):
            slice_index = len(slices_in) - 1

        # print("Slice index:", slice_index, "Length:", len(slices_in))

        layer_image = slices_in[slice_index]

        self.update_layer_image.emit(layer_image)

        self.update_exposure_time_indicator.emit(self.delta_time, self.get_exposure_time(layer_in))

        # print("Updating indicators")

        if self.delta_time > self.get_exposure_time(layer_in):
            print("Delta time has exceeded")

            if max_ink_number_in > 1:
                self.update_state.emit(StateControllerState.WASH)

                print("Changing to WASH")
                print(ink_number_in, ":", max_ink_number_in)

                if ink_number_in >= max_ink_number_in:
                    print("Resetting ink number")
                    progress_in.emit("Resetting ink number\n")
                    self.reset_ink_number.emit()

                    print("Updating layer")
                    progress_in.emit("Updating layer\n")
                    self.update_layer.emit()

                else:
                    print("Updating ink number")
                    progress_in.emit("Updating ink number\n")
                    self.update_ink_number.emit()

            else:
                self.update_state.emit(StateControllerState.GAP)

            self.reset_layer_image.emit()

            self.STATE = self.State.INIT

    def run(self, progress_in, layer_in, layer_image_in, ink_number_ink, max_ink_number_in, slice_frequency_in):
        match self.STATE:
            case self.State.INIT:
                self.init(progress_in, layer_in, layer_image_in)
            case self.State.EXPOSE:
                self.expose(progress_in, layer_in, layer_image_in, ink_number_ink, max_ink_number_in,
                            slice_frequency_in)
