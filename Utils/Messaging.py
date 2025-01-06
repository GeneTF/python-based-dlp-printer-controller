from PyQt6.QtWidgets import QMessageBox


class Messenger:
    def __init__(self, console_feed_in=None):
        self.console_feed = console_feed_in

    @staticmethod
    def generic_error(ex_in):
        ex = ex_in
        popup = QMessageBox()
        popup.setWindowTitle("Error found!")
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        popup.setText(message)
        popup.exec()

    @staticmethod
    def print_error(ex_in):
        ex = ex_in
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

    def error(self, message_in):
        self.popup = QMessageBox()
        self.popup.setWindowTitle("Error found!")
        self.popup.setText(message_in)
        self.popup.exec()

    def update_console(self, message_in):
        current_text = str(self.console_feed.toPlainText())
        self.console_feed.setText(current_text + message_in)
        self.console_feed.verticalScrollBar().setValue(self.console_feed.verticalScrollBar().maximum())
