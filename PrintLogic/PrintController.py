from PyQt6.QtCore import QObject, pyqtSignal
from MainWidgets.ExposureScheduleWidget import ExposureScheduleWidgetGUI
from MainWidgets.STLWidget import STLSelectorGUI
from MainWidgets.LayerImageWidget import LayerImageGUI
from MainWidgets.ConsoleWidget import ConsoleGUI
from MainWidgets.ParameterContainerWidget import ParameterContainerGUI
from PrintLogic import StateController
from PrintLogic.ControllerStates import PrintControllerState
import time


class PrintControl(QObject):
    finished = pyqtSignal()
    state_changed = pyqtSignal(object)
    progress = pyqtSignal(str)

    # Minimum time in seconds to sleep for loop to behave correctly
    min_time_to_sleep = 0.001

    def __init__(self, stl_selector_in, console_in, schedule_gui_in, layer_image_in, sys_param_in, print_param_in,
                 loc_param_in):
        super().__init__()
        self.stl_selector = stl_selector_in  # type: STLSelectorGUI.STLSelector
        self.console = console_in  # type: ConsoleGUI.Console
        self.schedule_gui = schedule_gui_in  # type: ExposureScheduleWidgetGUI.ExposureScheduleWidget
        self.layer_image = layer_image_in  # type: LayerImageGUI.LayerImageWidget
        self.sys_param = sys_param_in  # type: ParameterContainerGUI.ParameterContainer
        self.print_param = print_param_in  # type: ParameterContainerGUI.ParameterContainer
        self.loc_param = loc_param_in  # type: ParameterContainerGUI.ParameterContainer

        self.stl_lists = self.stl_selector.get_split_sorted_stls()

        self.STATE = PrintControllerState.IDLE
        self.state_controller = StateController.StateControl(self.console, self.schedule_gui, self.stl_selector,
                                                             self.layer_image)

        self.state_controller.gap.layer_height = float(self.sys_param.group.children()[1].param.text())
        self.state_controller.gap.um_per_step = float(self.sys_param.group.children()[6].param.text())

        self.state_controller.wash.layer_height = float(self.sys_param.group.children()[1].param.text())
        self.state_controller.wash.retraction_height = float(self.print_param.group.children()[2].param.text())
        self.state_controller.wash.um_per_step = float(self.sys_param.group.children()[6].param.text())

        self.state_controller.wash.tray_locations = self.stl_selector.get_tray_locations()

        self.state_controller.wash.wash_wait_time = float(self.print_param.group.children()[1].param.text())

        self.state_controller.max_z_pos = self.stl_selector.get_max_z_pos(
            float(self.sys_param.group.children()[1].param.text())
        )

        self.state_controller.finished.connect(self.stop_print)

    def start_print(self):
        self.STATE = PrintControllerState.PRINTING
        self.state_changed.emit(self.STATE)

        while self.STATE == PrintControllerState.PRINTING:
            # Progress is passed in as a parameter due to sequencing issues.
            # Hypothetically, if you make a signal in state controller called "progress"
            # and you connect it to progress here in print controller, whatever is emitted
            # in state controller will come AFTER whatever print controller emits.
            # You need to pass progress as an argument so that child functions emit progress
            # in a sequential manner.
            self.state_controller.run(self.progress)

            time.sleep(self.min_time_to_sleep)

        self.finished.emit()

    def stop_print(self):
        self.STATE = PrintControllerState.IDLE
        self.state_changed.emit(self.STATE)
