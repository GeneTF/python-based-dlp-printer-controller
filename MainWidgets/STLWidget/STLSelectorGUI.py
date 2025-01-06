from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QToolButton
from PyQt6.QtGui import QIcon

from Utils import Messaging
from MainWidgets.CustomWidgetGUI import CustomWidget
from MainWidgets.ParameterContainerWidget import ParameterContainerGUI
from Validators.Validator import IntValidator
from MainWidgets.STLWidget import TrimeshSlicer
import MainConstants

import trimesh


class STLSelector(CustomWidget):
    MAX_INK_NUMBER = 3
    MIN_INK_NUMBER = 1

    def __init__(self, sys_param_container_in, loc_param_in):
        super().__init__()
        self.fix_size_policy(self)

        # Is supposed to contain list of STL objects
        # It must be manually be set when the print button is called
        # This assumes that the user has added some amount of STL files to this widget
        self.stl_lists = []
        self.mesh_lists = []

        self.sys_param_container = sys_param_container_in  # type: ParameterContainerGUI.ParameterContainer
        self.loc_param = loc_param_in  # type: ParameterContainerGUI.ParameterContainer

        self.img_width = MainConstants.DEFAULT_PROJECTOR_X
        self.img_height = MainConstants.DEFAULT_PROJECTOR_Y

        self.um_per_px = MainConstants.DEFAULT_UM_PER_PX

        self.layer_height = MainConstants.DEFAULT_LAYER_HEIGHT

        self.slicer = TrimeshSlicer.Slicer()

        self.stl_selector_layout = QVBoxLayout()

        self.group = QGroupBox()
        self.group.setTitle("STL Selection")

        self.group_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        self.add_stl_button = QPushButton()
        self.preview = QPushButton("Preview")

        self.file_dialog = QFileDialog()

        self.set_up_widgets()
        self.set_up_layout()

        self.setEnabled(True)

    def set_up_widgets(self):
        self.group.setMinimumWidth(100)

        self.add_stl_button.setText("Add STL")
        self.fix_size_policy(self.add_stl_button)

        self.add_stl_button.clicked.connect(self.get_file_info)
        self.preview.clicked.connect(self.preview_all_meshes)

    def set_up_layout(self):
        self.group_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.button_layout.addWidget(self.add_stl_button)
        self.button_layout.addWidget(self.preview)
        self.button_layout.addStretch()
        self.group_layout.addLayout(self.button_layout)

        self.group.setLayout(self.group_layout)

        self.stl_selector_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.stl_selector_layout.addWidget(self.group)

        self.setLayout(self.stl_selector_layout)

    def set_img_size(self):
        self.project_x = self.sys_param_container.group.children()[3]  # type: ParameterContainerGUI.ParameterObject
        self.project_y = self.sys_param_container.group.children()[4]  # type: ParameterContainerGUI.ParameterObject

        self.img_width = int(self.project_x.param.text())
        self.img_height = int(self.project_y.param.text())

        self.slicer.img_width = self.img_width
        self.slicer.img_height = self.img_height

        if not self.is_empty():
            self.slicer.set_center_vector(self.get_all_meshes())

    def set_um_per_px(self):
        self.um_per_px = int(self.sys_param_container.group.children()[5].param.text())

        self.slicer.um_per_px = self.um_per_px

    def set_layer_height(self):
        self.layer_height = int(self.sys_param_container.group.children()[1].param.text())

        self.slicer.layer_height = self.layer_height

    def get_file_info(self):
        file_type = "stl(*.stl)"
        full_dir = self.file_dialog.getOpenFileName(filter=file_type)[0]
        file_name = full_dir.split('/')[-1]

        if full_dir != "":
            self.add_stl_obj(full_dir, file_name)

    def preview_all_meshes(self):
        mesh_list = self.get_all_meshes()

        self.slicer.preview_all_meshes(mesh_list)

    def add_stl_obj(self, full_dir_in, file_name_in):
        try:
            stl_obj = STLObject(full_dir_in, file_name_in)
            stl_obj.set_up_widgets()
            stl_obj.set_up_layout()
            stl_obj.set_validator(IntValidator(self.MIN_INK_NUMBER, self.MAX_INK_NUMBER, self.MIN_INK_NUMBER))
            stl_obj.close_button.clicked.connect(self.remove_stl_obj)
            self.group_layout.addWidget(stl_obj)
        except Exception as ex:
            messenger = Messaging.Messenger()
            messenger.generic_error(ex)

    def remove_stl_obj(self):
        try:
            self.sender().parent().deleteLater()
            self.group_layout.removeWidget(self.sender().parent())
        except Exception as ex:
            messenger = Messaging.Messenger()
            messenger.generic_error(ex)

    def is_empty(self):
        present = len(self.get_stls()) > 0
        return not present

    def is_stl_values_filled(self):
        for stl in self.get_stls():
            if stl.is_empty():
                return False

        return True

    def get_stls(self):
        stls = []

        for child in self.group.children():
            if isinstance(child, STLObject):
                stls.append(child)

        return stls

    def get_all_meshes(self):
        stls = self.get_stls()

        mesh_list = []
        stl: STLObject
        for stl in stls:
            mesh_list.append(stl.mesh)

        return mesh_list

    def get_sorted_stls(self):
        stls = self.get_stls()

        return sorted(stls, key=lambda stl: stl.ink_number.text())

    def get_split_sorted_stls(self):
        """
        Groups each stl object by their ink number into a list and returns a list containing each group.
        """
        stls = []
        stl_lists = []

        value = None

        for stl in self.get_sorted_stls():
            if value is None or value == stl.ink_number.text():
                value = stl.ink_number.text()
                stls.append(stl)

            else:
                stl_lists.append(stls)
                stls = []
                stls.append(stl)

        else:
            stl_lists.append(stls)

        return stl_lists

    def set_stl_lists(self):
        self.stl_lists = self.get_split_sorted_stls()

    def set_mesh_lists(self):
        if len(self.stl_lists) > 0:
            stl_lists = self.stl_lists
        else:
            stl_lists = self.get_split_sorted_stls()

        self.mesh_lists.clear()
        for stl_list in stl_lists:
            mesh_list = []

            for stl in stl_list:
                mesh_list.append(stl.mesh)

            self.mesh_lists.append(mesh_list)

    def set_center_vector(self):
        self.slicer.set_center_vector(self.get_all_meshes())

    def get_mesh_list(self, ink_number_in):
        self.set_mesh_lists()
        return self.mesh_lists[ink_number_in - 1]

    def max_ink_number(self):
        return len(self.stl_lists)

    def get_tray_locations(self):
        temp_locations = [self.loc_param.group.children()[i].param.text() for i in range(1, 5)]
        tray_locations = []

        for child in self.group.children():
            if isinstance(child, STLObject):
                tray_location = temp_locations[int(child.ink_number.text()) - 1]

                if tray_location not in tray_locations:
                    tray_locations.append(float(tray_location))

        return sorted(tray_locations) + [float(temp_locations[-1])]

    def get_max_layers(self):
        return self.slicer.get_max_layers(self.get_all_meshes())

    def get_max_z_pos(self, layer_height_in):
        return (self.get_max_layers()) * layer_height_in * 10**-3

    def slice(self, ink_number_in, layer_in):
        bitmap = self.slicer.slice(layer_in, self.get_mesh_list(ink_number_in))
        img = self.slicer.convert_to_pix(bitmap)
        return img

    def get_slices(self, ink_number_in, layer_in, max_cure_depth_in, slice_count_in, exposure_time_in):
        return self.slicer.get_slices(layer_in, self.get_mesh_list(ink_number_in), max_cure_depth_in, slice_count_in,
                                      exposure_time_in)


class STLObject(CustomWidget):
    def __init__(self, full_dir_in, file_name_in):
        super().__init__()
        self.obj_layout = QHBoxLayout()

        self.close_button = QToolButton()
        self.close_button_icon = QIcon.fromTheme('edit-delete')
        self.close_button.setIcon(self.close_button_icon)

        self.full_dir = full_dir_in

        self.file_name = QLabel()
        self.file_name.setText(file_name_in)

        # Load mesh as a Trimesh
        self.mesh = trimesh.load_mesh(self.full_dir)

        self.ink_number = QLineEdit()

    def set_up_widgets(self):
        self.fix_size_policy(self.file_name)

        self.ink_number.setMaximumWidth(20)
        self.ink_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ink_number.setText("1")

    def set_up_layout(self):
        self.obj_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.obj_layout.setSpacing(0)
        self.obj_layout.setContentsMargins(0, 0, 0, 0)

        self.obj_layout.addWidget(self.close_button)
        self.obj_layout.addWidget(self.ink_number)
        self.obj_layout.addWidget(self.file_name)

        self.setLayout(self.obj_layout)

    def set_validator(self, validator_in):
        validator_in.fixup_signal.connect(self.fixup)
        self.ink_number.setValidator(validator_in)

    def fixup(self, input_in):
        self.ink_number.setText(str(input_in))

    def is_empty(self):
        return self.ink_number.text() == ""
