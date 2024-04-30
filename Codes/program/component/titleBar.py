from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QIcon
import os

class TitleBar(QWidget):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.setAutoFillBackground(True)
        self.setFixedHeight(30)

        # 加载 QSS 文件
        self.load_qss("component\\qss\\titleBar.qss")

        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 添加标题文本
        self.titleLabel = QLabel("Audio Player", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.titleLabel)

        # 添加最小化按钮
        self.minimizeButton = QPushButton(self)
        self.minimizeButton.setIcon(QIcon("path/to/minimize_icon.png"))
        self.minimizeButton.clicked.connect(self.parent().showMinimized)
        layout.addWidget(self.minimizeButton)

        # 添加最大化/还原按钮
        self.maximizeButton = QPushButton(self)
        self.maximizeButton.setIcon(QIcon("path/to/maximize_icon.png"))
        self.maximizeButton.clicked.connect(self.toggleMaximize)
        layout.addWidget(self.maximizeButton)

        # 添加关闭按钮
        self.closeButton = QPushButton(self)
        self.closeButton.setIcon(QIcon("path/to/close_icon.png"))
        self.closeButton.clicked.connect(self.parent().close)
        layout.addWidget(self.closeButton)

        # 添加事件过滤器
        self.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched == self and event.type() == QEvent.MouseButtonPress:
            self.dragPosition = event.globalPos() - self.mainWindow.frameGeometry().topLeft()
            return True
        elif watched == self and event.type() == QEvent.MouseMove:
            if event.buttons() == Qt.LeftButton:
                self.mainWindow.move(event.globalPos() - self.dragPosition)
                return True
        return super().eventFilter(watched, event)

    def load_qss(self, qss_file):
        qss_path = os.path.join(self.parent().baseDir, qss_file)
        with open(qss_path, "r") as f:
            self.setStyleSheet(f.read())

    def toggleMaximize(self):
        if self.mainWindow.isMaximized():
            self.mainWindow.showNormal()
            self.maximizeButton.setIcon(QIcon("path/to/maximize_icon.png"))
        else:
            self.mainWindow.showMaximized()
            self.maximizeButton.setIcon(QIcon("path/to/restore_icon.png"))