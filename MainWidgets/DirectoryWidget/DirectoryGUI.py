from PyQt6.QtWidgets import QWidget, QGridLayout, QLineEdit, QToolButton, QFileDialog, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from MainWidgets.CustomWidgetGUI import CustomWidget


class DirectoryWidget(CustomWidget):
    def __init__(self, label_in, filter_in):
        super().__init__()

        # File filter
        self.file_filter = filter_in + "(*." + filter_in + ")"

        # Initialize layout
        self.dir_layout = QGridLayout()

        # Initialize widgets
        self.file_dir = QLineEdit()
        self.file_dir.setReadOnly(True)
        self.tool_button = QToolButton()
        self.file_dialog = QFileDialog()
        self.file_dir_label = QLabel()

        # Set up icons
        folder_icon = QIcon.fromTheme('folder-open')
        self.tool_button.setIcon(folder_icon)

        # Set text for widgets
        self.file_dir_label.setText(label_in)

        # Set up layout
        self.dir_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.dir_layout.addWidget(self.file_dir_label, 0, 0, 1, 2)
        self.dir_layout.addWidget(self.tool_button, 1, 0)
        self.dir_layout.addWidget(self.file_dir, 1, 1)

        # Set layout of custom group box
        self.setLayout(self.dir_layout)

        self.setEnabled(False)

    def get_file_name(self):
        print(self.file_filter)
        self.file_dir.setText(self.file_dialog.getOpenFileName(filter=self.file_filter)[0])

    def get_folder_name(self):
        self.file_dir.setText(self.file_dialog.getExistingDirectory())


class FolderDirectoryWidget(DirectoryWidget):
    def __init__(self, label_in, filter_in):
        super().__init__(label_in, filter_in)

        self.tool_button.clicked.connect(self.get_folder_name)


class FileDirectoryWidget(DirectoryWidget):
    def __init__(self, label_in, filter_in):
        super().__init__(label_in, filter_in)

        self.tool_button.clicked.connect(self.get_file_name)
