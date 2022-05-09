from functools import partial

from PyQt5.QtWidgets import QMessageBox, QWidget
from qtpy.QtCore import Slot


@Slot()
def showDisplay(display: QWidget):
    display.show()

    # brings the display to the front
    display.raise_()

    # gives the display focus
    display.activateWindow()


def make_error_popup(title, expert_edmbutton, exception, action_func):
    popup = QMessageBox()
    popup.setIcon(QMessageBox.Critical)
    popup.setWindowTitle(title)
    popup.setText(
        '{error}\nPlease check expert screen and select from the options below'.format(error=exception))
    popup.addButton('Abort', QMessageBox.RejectRole)
    popup.addButton('Acknowledge manual completion and continue', QMessageBox.AcceptRole)
    popup.addButton(expert_edmbutton, QMessageBox.ActionRole)
    popup.buttonClicked.connect(partial(action_func, popup))
    popup.exec()


def make_info_popup(text):
    popup = QMessageBox()
    popup.setIcon(QMessageBox.Information)
    popup.setText(text)
    popup.exec()