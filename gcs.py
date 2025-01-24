import sys
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
from screeninfo import get_monitors, Monitor



class VideoWindow(QtWidgets.QWidget):
    def __init__(self, width: int, height: int):
        super().__init__()

        # Create a label that will display the images
        self.image_label = QtWidgets.QLabel(self)
        self.setWindowTitle('OpenCV + PyQt5 Live Feed')
        self.display_window(get_monitors(), width, height)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.image_label)

        # Set up the video capture object
        self.cap = cv2.VideoCapture('http://192.168.81.123:81/stream')  # 0 is the default camera
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

        # Set up a timer to update the image every so often
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # milliseconds

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the image from BGR (OpenCV format) to RGB (Qt format)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), QtCore.Qt.KeepAspectRatio)
            self.image_label.setPixmap(QtGui.QPixmap.fromImage(p))
            
    def display_window(self, monitors: list[Monitor], widht: int, height: int) -> None:
        coordinats = {
            "x": (monitors[0].width - widht)//2,
            "y": (monitors[0].height - height)//2
        }
        self.setGeometry(coordinats['x'], coordinats['y'], widht, height)

    def closeEvent(self, event):
        self.cap.release()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = VideoWindow(800, 600)
    main_window.show()
    sys.exit(app.exec_())
