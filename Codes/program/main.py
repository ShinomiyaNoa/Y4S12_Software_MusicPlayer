from PySide6.QtGui import QCloseEvent, QMouseEvent, QCursor
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QRubberBand
from PySide6.QtCore import Qt, QRect
from component.titleBar import TitleBar
from component.musicPlayer import MusicPlayer
import sys
import os

class MainWindow(QMainWindow):
    def __init__(self, master=None):
        super().__init__(flags=Qt.FramelessWindowHint)
        self.setGeometry(0, 0, 1000, 700)
        self.baseDir = os.path.dirname(os.path.abspath(__file__))
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.dragging_top = False
        self.dragging_bottom = False
        self.dragging_left = False
        self.dragging_right = False
        self.dragging_window = False

        self.thread_stop_flag = False

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

        layout.setStretchFactor(self.musicPlayer, 1)

        with open(os.path.join(self.baseDir, 'main.qss'), "r") as f:
            self.setStyleSheet(f.read())

    def closeEvent(self, event: QCloseEvent) -> None:
        self.thread_stop_flag = True
        return super().closeEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.rect().adjusted(5, 5, -5, -5).contains(event.pos()):
                self.dragging_window = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
            else:
                self.dragging_window = False
                self.dragging_top = event.pos().y() < 5
                self.dragging_bottom = event.pos().y() > self.height() - 5
                self.dragging_left = event.pos().x() < 5
                self.dragging_right = event.pos().x() > self.width() - 5
                if self.dragging_top or self.dragging_bottom or self.dragging_left or self.dragging_right:
                    self.rubberBand.setGeometry(QRect(self.mapToGlobal(self.rect().topLeft()), self.mapToGlobal(self.rect().bottomRight())))
                    self.rubberBand.show()
                event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            if self.dragging_window:
                self.move(event.globalPos() - self.drag_position)
                event.accept()
            elif self.dragging_top or self.dragging_bottom or self.dragging_left or self.dragging_right:
                if self.dragging_top:
                    self.rubberBand.setGeometry(QRect(self.mapToGlobal(self.rect().topLeft()), self.mapToGlobal(event.pos())))
                elif self.dragging_bottom:
                    self.rubberBand.setGeometry(QRect(self.mapToGlobal(self.rect().topLeft()), self.mapToGlobal(event.pos())))
                elif self.dragging_left:
                    self.rubberBand.setGeometry(QRect(self.mapToGlobal(self.rect().topLeft()), self.mapToGlobal(event.pos())))
                elif self.dragging_right:
                    self.rubberBand.setGeometry(QRect(self.mapToGlobal(self.rect().topLeft()), self.mapToGlobal(event.pos())))
                event.accept()
        else:
            if event.pos().y() < 5:
                self.setCursor(QCursor(Qt.SizeVerCursor))
            elif event.pos().y() > self.height() - 5:
                self.setCursor(QCursor(Qt.SizeVerCursor))
            elif event.pos().x() < 5:
                self.setCursor(QCursor(Qt.SizeHorCursor))
            elif event.pos().x() > self.width() - 5:
                self.setCursor(QCursor(Qt.SizeHorCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.dragging_window:
                self.dragging_window = False
            elif self.dragging_top or self.dragging_bottom or self.dragging_left or self.dragging_right:
                self.dragging_top = False
                self.dragging_bottom = False
                self.dragging_left = False
                self.dragging_right = False
                self.resize(self.rubberBand.size())
                self.rubberBand.hide()
            event.accept()

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()