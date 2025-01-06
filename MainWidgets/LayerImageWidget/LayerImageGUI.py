from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLayout, QLabel
from PyQt6.QtCore import Qt
from MainWidgets.CustomWidgetGUI import CustomWidget
from MainWidgets.ParameterContainerWidget import ParameterContainerGUI
from Utils import Imaging
import MainConstants
import numpy as np


class LayerImageWidget(CustomWidget):
    def __init__(self, sys_param_container_in):
        super().__init__()

        self.widget_layout = QHBoxLayout()
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.show_layer = QPushButton("Project")
        self.show_layer.clicked.connect(self.show_layer_image)

        self.fullscreen = QPushButton("Fullscreen")
        self.fullscreen.clicked.connect(self.show_fullscreen)

        self.close = QPushButton("Close")
        self.close.clicked.connect(self.close_layer_image)

        self.sys_param_container = sys_param_container_in  # type: ParameterContainerGUI.ParameterContainer

        self.img_width = MainConstants.DEFAULT_PROJECTOR_X
        self.img_height = MainConstants.DEFAULT_PROJECTOR_Y

        self.widget_layout.addWidget(self.show_layer)
        self.widget_layout.addWidget(self.fullscreen)
        self.widget_layout.addWidget(self.close)

        self.setLayout(self.widget_layout)

        self.layer_image_label = QLabel()
        self.reset_image()

        self.layer_image_window = CustomWidget()

        self.layer_image_layout = QHBoxLayout()
        self.layer_image_layout.setSpacing(0)
        self.layer_image_layout.setContentsMargins(0, 0, 0, 0)
        self.layer_image_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.layer_image_layout.addWidget(self.layer_image_label)

        self.layer_image_window.setLayout(self.layer_image_layout)

        self.setEnabled(False)

    def set_img_size(self):
        self.project_x = self.sys_param_container.group.children()[3]  # type: ParameterContainerGUI.ParameterObject
        self.project_y = self.sys_param_container.group.children()[4]  # type: ParameterContainerGUI.ParameterObject

        self.img_width = int(self.project_x.param.text())
        self.img_height = int(self.project_y.param.text())

        self.reset_image()

    def show_layer_image(self):
        self.layer_image_window.setLayout(self.layer_image_layout)
        self.layer_image_window.showNormal()

    def show_fullscreen(self):
        self.layer_image_window.showFullScreen()

    def close_layer_image(self):
        self.layer_image_window.close()

    def set_layer_image(self, img_in):
        self.layer_image_label.setPixmap(img_in)

    def reset_image(self):
        img = np.zeros((self.img_height, self.img_width, 3), np.uint8)
        pixmap = Imaging.convert_cv_qt(self.img_width, self.img_height, img)
        self.layer_image_label.setPixmap(pixmap)
