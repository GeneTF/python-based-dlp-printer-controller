from PyQt6.QtWidgets import QWidget, QHBoxLayout, QMainWindow, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from MainWidgets.ConsoleWidget import ConsoleGUI
from MainWidgets.ToolbarWidget import ToolbarGUI
from MainWidgets.MotorControllerWidget import MotorControllerGUI
from MainWidgets.STLWidget import STLSelectorGUI
from MainWidgets.ParameterContainerWidget import ParameterContainerGUI
from MainWidgets.DirectoryWidget import DirectoryGUI
from MainWidgets.ExposureScheduleWidget import ExposureScheduleWidgetGUI
from MainWidgets.PrintWidget import PrintGUI
from MainWidgets.LayerImageWidget import LayerImageGUI
import MainConstants

from Validators.Validator import IntValidator, DoubleValidator

from enum import Enum


class MainWidget(QWidget):
    state_changed = pyqtSignal()

    class State(Enum):
        UNCONNECTED = 0
        IDLE = 1
        PRINTING = 2

    def __init__(self):
        super().__init__()
        self.STATE = self.State.UNCONNECTED

        self.main_layout = QHBoxLayout()

        self.console = ConsoleGUI.Console()
        self.motor_controller = MotorControllerGUI.MotorController(self.console)
        self.toolbar = ToolbarGUI.Toolbar(self.console, self.motor_controller)
        self.exp_time_csv = DirectoryGUI.FileDirectoryWidget("Exposure Mask CSV", "csv")
        self.sys_param_container = ParameterContainerGUI.ParameterContainer()
        self.exposure_schedule = ExposureScheduleWidgetGUI.ExposureScheduleWidget()
        self.loc_param_container = ParameterContainerGUI.ParameterContainer()
        self.print_param_container = ParameterContainerGUI.ParameterContainer()
        self.layer_image_gui = LayerImageGUI.LayerImageWidget(self.sys_param_container)
        self.stl_selector = STLSelectorGUI.STLSelector(self.sys_param_container, self.loc_param_container)

        self.print_widget = PrintGUI.PrintWidget(self.stl_selector, self.console, self.exposure_schedule,
                                                 self.layer_image_gui, self.toolbar, self.motor_controller,
                                                 self.sys_param_container, self.print_param_container,
                                                 self.loc_param_container)

        self.set_up_widgets()
        self.set_up_layout()

    def set_up_widgets(self):
        self.console.setFixedWidth(500)

        self.exp_time_csv.setMaximumWidth(500)

        self.sys_param_container.setMaximumWidth(500)
        self.sys_param_container.setMaximumHeight(300)
        self.sys_param_container.set_max_param_width(40)

        self.sys_param_container.add_widget("Layer Height (μm)",
                                            MainConstants.DEFAULT_LAYER_HEIGHT,
                                            IntValidator(5, 1000, MainConstants.DEFAULT_LAYER_HEIGHT))

        self.sys_param_container.add_widget("Cure Depth (μm)",
                                            "100",
                                            IntValidator(5, 1000, 100))

        self.sys_param_container.add_widget("Projector X Resolution (px)",
                                            MainConstants.DEFAULT_PROJECTOR_X,
                                            IntValidator(1, 8096, MainConstants.DEFAULT_PROJECTOR_X),
                                            [self.layer_image_gui.set_img_size,
                                             self.stl_selector.set_img_size])

        self.sys_param_container.add_widget("Projector Y Resolution (px)",
                                            MainConstants.DEFAULT_PROJECTOR_Y,
                                            IntValidator(1, 8096, MainConstants.DEFAULT_PROJECTOR_Y),
                                            [self.layer_image_gui.set_img_size,
                                             self.stl_selector.set_img_size])

        self.sys_param_container.add_widget("Microns per Pixel (μm/px)",
                                            MainConstants.DEFAULT_UM_PER_PX,
                                            IntValidator(1, 1000, MainConstants.DEFAULT_UM_PER_PX),
                                            [self.stl_selector.set_um_per_px])

        self.sys_param_container.add_widget("Microns per Step (μm/step)",
                                            "500",
                                            IntValidator(1, 1000, 250))

        self.sys_param_container.group.setTitle("System Parameters")

        self.layer_image_gui.set_img_size()

        self.loc_param_container.setMaximumWidth(500)
        self.loc_param_container.set_max_param_width(40)
        self.loc_param_container.add_widget("Ink Tray 1 Location",
                                            MainConstants.DEFAULT_TRAY_1_LOC,
                                            DoubleValidator(0, 50, 1, MainConstants.DEFAULT_TRAY_1_LOC))
        self.loc_param_container.add_widget("Ink Tray 2 Location",
                                            MainConstants.DEFAULT_TRAY_2_LOC,
                                            DoubleValidator(0, 50, 1, MainConstants.DEFAULT_TRAY_2_LOC))
        self.loc_param_container.add_widget("Ink Tray 3 Location",
                                            MainConstants.DEFAULT_TRAY_3_LOC,
                                            DoubleValidator(0, 50, 1, MainConstants.DEFAULT_TRAY_3_LOC))
        self.loc_param_container.add_widget("Washing Tray Location",
                                            MainConstants.DEFAULT_WASH_TRAY_LOC,
                                            DoubleValidator(0, 50, 1, MainConstants.DEFAULT_WASH_TRAY_LOC))
        self.loc_param_container.group.setTitle("Location Parameters")

        self.print_param_container.setMaximumWidth(500)
        self.print_param_container.set_max_param_width(40)

        self.print_param_container.add_widget("Wash Time (s)",
                                              MainConstants.DEFAULT_WASH_WAIT,
                                              IntValidator(0, 60, MainConstants.DEFAULT_WASH_WAIT))

        self.print_param_container.add_widget("Retraction Height (mm)",
                                              MainConstants.DEFAULT_RETRACTION_HEIGHT,
                                              DoubleValidator(40, 60, 1, MainConstants.DEFAULT_RETRACTION_HEIGHT))

        self.print_param_container.group.setTitle("Print Parameters")

        self.toolbar.connect_button.clicked.connect(self.connect)

        self.print_widget.print_button.clicked.connect(self.init_print)

        self.state_changed.connect(self.update_ui)

    def set_up_layout(self):
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        col1 = QVBoxLayout()
        col2 = QVBoxLayout()
        col3 = QVBoxLayout()
        col4 = QVBoxLayout()

        col1.addWidget(self.toolbar)
        col1.addWidget(self.motor_controller)
        col1.addWidget(self.console)

        col2.setAlignment(Qt.AlignmentFlag.AlignTop)
        col2.addWidget(self.print_widget)
        col2.addWidget(self.print_param_container)
        col2.addWidget(self.sys_param_container)
        col2.addWidget(self.loc_param_container)
        col2.addWidget(self.layer_image_gui)
        col2.addStretch()

        col3.addWidget(self.exp_time_csv)
        col3.addWidget(self.exposure_schedule)
        col3.addStretch()

        col4.addWidget(self.stl_selector)

        self.main_layout.addLayout(col1)
        self.main_layout.addLayout(col2)
        self.main_layout.addLayout(col3)
        self.main_layout.addLayout(col4)
        self.main_layout.addStretch(1)

        self.setLayout(self.main_layout)

    @pyqtSlot()
    def connect(self):
        self.toolbar.initialize_worker()
        self.toolbar.get_worker().connected.connect(self.update_ui_by_usb)
        self.toolbar.connect()

    def init_print(self):
        proceed = self.print_widget.init_print()

        if proceed:
            self.start_print()

    def start_print(self):
        self.print_widget.initialize_worker()
        self.print_widget.get_worker().state_changed.connect(self.update_ui_by_print)
        self.print_widget.start_print()

    def update_ui_by_usb(self, usb_connected_in):
        if usb_connected_in:
            self.STATE = self.State.IDLE
        else:
            self.STATE = self.State.UNCONNECTED

        self.state_changed.emit()

    def update_ui_by_print(self, state_in):
        if state_in == self.print_widget.print_controller.STATE.PRINTING:
            self.STATE = self.State.PRINTING
        else:
            self.STATE = self.State.IDLE

        self.state_changed.emit()

    def update_ui(self):
        if self.STATE == self.State.IDLE:
            self.console.setEnabled(True)
            self.toolbar.setEnabled(False)
            self.motor_controller.setEnabled(True)
            self.stl_selector.setEnabled(True)
            self.exp_time_csv.setEnabled(True)
            self.sys_param_container.setEnabled(True)
            self.exposure_schedule.setEnabled(True)
            self.print_param_container.setEnabled(True)

            self.print_widget.setEnabled(True)
            self.print_widget.print_button.setEnabled(True)
            self.print_widget.stop.setEnabled(False)
            self.print_widget.pause.setEnabled(False)
            self.print_widget.resume.setEnabled(False)

            self.loc_param_container.setEnabled(True)

            self.layer_image_gui.setEnabled(True)

        elif self.STATE == self.State.PRINTING:
            self.console.setEnabled(True)
            self.toolbar.setEnabled(False)
            self.motor_controller.setEnabled(False)
            self.stl_selector.setEnabled(False)
            self.exp_time_csv.setEnabled(False)
            self.sys_param_container.setEnabled(False)
            self.exposure_schedule.setEnabled(False)
            self.loc_param_container.setEnabled(False)
            self.print_param_container.setEnabled(False)

            self.print_widget.print_button.setEnabled(False)
            self.print_widget.stop.setEnabled(True)

            self.layer_image_gui.setEnabled(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom DLP App")
        self.main_widget = MainWidget()

        self.setCentralWidget(self.main_widget)
