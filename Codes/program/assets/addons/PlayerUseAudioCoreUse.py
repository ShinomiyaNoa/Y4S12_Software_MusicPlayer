# mainTest.py

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication, QSlider, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from program.core.AudioCore import AudioPlayer
import sys
import os

class MainWindow(QMainWindow):

    def __init__(self, master=None):
        super().__init__(master)
        self.setWindowTitle("Audio Player")

        self.audio_player = AudioPlayer()

        self.create_ui()

    def create_ui(self):
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.hbuttonbox = QHBoxLayout()
        self.playbutton = QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.audio_player.play_pause)

        self.stopbutton = QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.audio_player.stop)

        self.filebutton = QPushButton("Select File")
        self.hbuttonbox.addWidget(self.filebutton)
        self.filebutton.clicked.connect(self.select_file)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QSlider(Qt.Orientation.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.audio_player.get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.audio_player.set_volume)

        self.positionslider = QSlider(Qt.Orientation.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.setValue(self.audio_player.get_position())
        self.positionslider.sliderMoved.connect(self.audio_player.set_position)
        self.hbuttonbox.addWidget(self.positionslider)

        self.widget.setLayout(self.hbuttonbox)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

    def select_file(self):
        dialog_txt = "Choose Audio File"
        filename, _ = QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        if not filename:
            return
        self.audio_player.open_file(filename)

    def update_ui(self):
        self.volumeslider.setValue(self.audio_player.get_volume())
        self.positionslider.setValue(self.audio_player.get_position())

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()