import sys
from PyQt5 import QtWidgets, uic
import cv2
from pathlib import Path
from ColorFinder import ColorFinder
import RPi.GPIO as GPIO
import time
import subprocess


class HomeWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(HomeWindow, self).__init__(*args, **kwargs)

        self.ui = uic.loadUi('GlucoHealthScreen.ui', self)
        self.initui()

        # Create Variables
        self._filename = None
        self._ColorFinder = None

    def initui(self):
        """Button Connection"""
        self.startButton.clicked.connect(self.start)
        #self.stopButton.clicked.connect(self.stop)

    def start(self):
        self.load_file()
        self._ColorFinder = ColorFinder()
        self._ColorFinder.findBin(self._filename)
        label = str(self._ColorFinder.colorBin)
        self.displayLabel.setText(label)

    def load_file(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        led = 4
        GPIO.setup(led,GPIO.OUT)

        GPIO.output(led,1)
        time.sleep(5)

        cam_port = 0
        cam = cv2.VideoCapture(cam_port)
        result, image = cam.read()

        if result:
            cv2.imwrite("test.png", image)

        self._filename = "test.png"

        GPIO.output(led, 0)

    def stop(self):
        subprocess.Popen(['sudo', 'shutdown', '-r', 'now'])



# run the pyqt code
def main():
    app = QtWidgets.QApplication(sys.argv)
    w = HomeWindow()
    w.setWindowTitle('Test')
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
