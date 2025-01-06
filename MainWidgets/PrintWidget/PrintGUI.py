from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

import numpy as np

from PrintLogic import PrintController
from MainWidgets.CustomWidgetGUI import CustomWidget
from Utils import Messaging
from MainWidgets.STLWidget import STLSelectorGUI
from MainWidgets.ConsoleWidget import ConsoleGUI
from MainWidgets.ExposureScheduleWidget import ExposureScheduleWidgetGUI
from MainWidgets.LayerImageWidget.LayerImageGUI import LayerImageWidget
from MainWidgets.ToolbarWidget import ToolbarGUI
from MainWidgets.MotorControllerWidget import MotorControllerGUI
from MainWidgets.ParameterContainerWidget import ParameterContainerGUI
from Utils import Imaging


class PrintWidget(CustomWidget):
    stop_print = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, stl_selector_in, console_in, schedule_gui_in, layer_image_gui_in, toolbar_in,
                 motor_controller_in, sys_param_container_in, print_param_in, loc_param_in):
        super().__init__()
        self.stl_selector = stl_selector_in  # type: STLSelectorGUI.STLSelector
        self.console = console_in  # type: ConsoleGUI.Console
        self.schedule_gui = schedule_gui_in  # type: ExposureScheduleWidgetGUI.ExposureScheduleWidget
        self.layer_image_gui = layer_image_gui_in  # type: LayerImageWidget
        self.toolbar = toolbar_in  # type: ToolbarGUI.Toolbar
        self.motor_controller = motor_controller_in  # type: MotorControllerGUI.MotorController
        self.sys_param_container = sys_param_container_in  # type:ParameterContainerGUI.ParameterContainer
        self.print_param = print_param_in  # type:ParameterContainerGUI.ParameterContainer
        self.loc_param = loc_param_in  # type:ParameterContainerGUI.ParameterContainer

        self.messenger = Messaging.Messenger(self.console.console_feed)

        self.widget_layout = QHBoxLayout()

        self.print_button = QPushButton()
        self.print_button.setText("Print")

        self.stop = QPushButton()
        self.stop.setText("Stop")

        self.resume = QPushButton()
        self.resume.setText("Resume")

        self.pause = QPushButton()
        self.pause.setText("Pause")

        self.set_up_widgets()
        self.set_up_layout()

        self.setEnabled(False)

    def set_up_widgets(self):
        self.error.connect(self.messenger.error)

    def set_up_layout(self):
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.widget_layout.addWidget(self.print_button)
        self.widget_layout.addWidget(self.stop)

        self.widget_layout.addStretch()

        self.widget_layout.addWidget(self.resume)
        self.widget_layout.addWidget(self.pause)

        self.setLayout(self.widget_layout)

    def initialize_worker(self):
        self.thread = QThread()
        self.print_controller = PrintController.PrintControl(self.stl_selector, self.console, self.schedule_gui,
                                                             self.layer_image_gui, self.sys_param_container,
                                                             self.print_param, self.loc_param)

        self.print_controller.state_controller.wash.current_x_pos = float(
            self.motor_controller.motor_controller_worker.get_x_pos()
        )

        print("Current x pos:", self.print_controller.state_controller.wash.current_x_pos)

        self.motor_controller.motor_controller_worker.reset_z_motor()

        self.print_controller.state_controller.current_z_pos = float(
            self.motor_controller.motor_controller_worker.get_z_pos()
        )

        self.motor_controller.motor_controller_worker.update_z_pos.connect(
            self.print_controller.state_controller.update_z_pos
        )

        self.print_controller.state_controller.update_z_pos_indicator.connect(self.update_z_pos_indicator)

        self.print_controller.state_controller.update_ink_number_indicator.connect(self.update_ink_number_indicator)
        self.print_controller.state_controller.update_layer_number_indicator.connect(self.update_layer_number_indicator)
        self.print_controller.state_controller.expose.update_exposure_time_indicator.connect(
            self.update_exposure_time_indicator
        )
        self.print_controller.state_controller.expose.update_layer.connect(
            self.print_controller.state_controller.update_layer
        )
        self.print_controller.state_controller.expose.reset_ink_number.connect(
            self.print_controller.state_controller.reset_ink_number
        )
        self.print_controller.state_controller.expose.reset_layer_image.connect(
            self.layer_image_gui.reset_image
        )

        self.print_controller.state_controller.gap.move_z_motor.connect(self.move_z_motor)
        self.print_controller.state_controller.gap.finish_moves.connect(
            self.motor_controller.motor_controller_worker.update_gap
        )
        self.motor_controller.motor_controller_worker.update_gap_signal.connect(
            self.print_controller.state_controller.gap.close
        )
        self.print_controller.state_controller.gap.update_layer.connect(
            self.print_controller.state_controller.update_layer
        )
        self.print_controller.state_controller.gap.change_state.connect(
            self.print_controller.state_controller.change_state
        )
        self.print_controller.state_controller.gap.update_z_pos.connect(
            self.motor_controller.motor_controller_worker.get_current_z
        )

        self.motor_controller.motor_controller_worker.update_wash_signal.connect(
            self.print_controller.state_controller.wash.update
        )
        self.print_controller.state_controller.wash.finish_moves_signal.connect(
            self.motor_controller.motor_controller_worker.update_wash
        )
        self.print_controller.state_controller.wash.write_command.connect(
            self.motor_controller.motor_controller_worker.write_command
        )
        self.print_controller.state_controller.wash.change_state.connect(
            self.print_controller.state_controller.change_state
        )
        self.print_controller.state_controller.wash.update_z_pos.connect(
            self.motor_controller.motor_controller_worker.get_current_z
        )

        try:
            self.print_controller.state_controller.expose.update_layer_image.connect(self.update_layer_image)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

        """
        The stop button is connected to stop thread function.
        The stop thread function emits the stop print signal in this class.
        The stop print signal is connected to stop print function in the printer controller class.
        In this way, the printer controller can stop the print.
        These connections must be made BEFORE moving the print controller to the thread.
        """
        self.stop.clicked.connect(self.stop_thread)
        self.stop_print.connect(self.print_controller.stop_print)

        self.print_controller.progress.connect(self.messenger.update_console)

        self.print_controller.moveToThread(self.thread)

    def get_worker(self):
        return self.print_controller

    def init_print(self):
        stl_present = not self.stl_selector.is_empty()

        init_conditions = [stl_present]

        proceed = all(init_conditions)

        if not proceed:
            if not stl_present:
                self.error.emit("Please select an STL!")

        return proceed

    def start_print(self):
        try:
            self.thread.started.connect(self.print_controller.start_print)
            self.print_controller.finished.connect(self.thread.quit)
            self.print_controller.finished.connect(self.print_controller.deleteLater)
            self.print_controller.finished.connect(self.layer_image_gui.reset_image)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

            self.print_button.setEnabled(False)

            self.thread.finished.connect(
                lambda: self.print_button.setEnabled(True)
            )

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

    def stop_thread(self):
        self.stop_print.emit()

    def update_exposure_time_indicator(self, delta_time_in, total_time_in):
        self.console.layer_indicator.exposure_time.update_indicator(f'{delta_time_in:.1f}', total_time_in)

    def update_ink_number_indicator(self, ink_number_in, max_ink_number_in):
        self.console.layer_indicator.ink_number.update_indicator(ink_number_in, max_ink_number_in)

    def update_layer_number_indicator(self, layer_number_in, max_layer_number_in):
        self.console.layer_indicator.layer_number.update_indicator(layer_number_in, max_layer_number_in)

    def update_z_pos_indicator(self, z_pos_in, max_z_pos_in):
        self.console.layer_indicator.z_motor_position.update_indicator(f'{z_pos_in:.2f}', f'{max_z_pos_in:.2f}')

    def update_layer_image(self, layer_image_in):
        self.layer_image_gui.set_layer_image(layer_image_in)

    def move_x_motor(self, pos_in, feedrate_in, relative_in):
        self.motor_controller.motor_controller_worker.move_x_motor(pos_in, feedrate_in, relative_in)

    def move_z_motor(self, pos_in, feedrate_in, relative_in):
        self.motor_controller.motor_controller_worker.move_z_motor(pos_in, feedrate_in, relative_in)
