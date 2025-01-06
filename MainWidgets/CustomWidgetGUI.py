from PyQt6.QtWidgets import QWidget, QSizePolicy


class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()

    @staticmethod
    def fix_size_policy(widget_in):
        policy = widget_in.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        widget_in.setSizePolicy(policy)
