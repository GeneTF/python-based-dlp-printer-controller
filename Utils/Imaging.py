from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import cv2


# Props to https://imagetracking.org.uk/2020/12/displaying-opencv-images-in-pyqt/
def convert_cv_qt(width, height, cv_img):
    """Convert from an opencv image to QPixmap"""
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage().format().Format_RGB888)
    p = convert_to_qt_format.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)
    return QPixmap.fromImage(p)
