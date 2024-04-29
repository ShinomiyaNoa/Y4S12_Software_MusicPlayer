from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout
from PySide6.QtCore import Qt
from component.titleBar import TitleBar
from component.musicPlayer import MusicPlayer
import sys
import json
import os

class MainWindow(QMainWindow):
    def __init__(self, master=None):
        super().__init__(flags=Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 1200, 700)
        self.baseDir = os.path.dirname(os.path.abspath(__file__))

        # 创建主窗口布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        self.titleBar = TitleBar(self, self)
        self.setMenuWidget(self.titleBar)
        layout.addWidget(self.titleBar)

        # 音乐播放器
        self.musicPlayer = MusicPlayer(self, self)
        layout.addWidget(self.musicPlayer)

        

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()