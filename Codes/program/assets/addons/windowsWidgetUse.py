from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QToolBar, QComboBox, QGridLayout
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #  创建主布局
        main_layout = QVBoxLayout()

        #  创建菜单和工具栏行布局
        menu_and_widget_row = QHBoxLayout()
        menu_bar = QToolBar()
        menu_bar.addWidget(QLabel("Menu Bar"))
        menu_and_widget_row.addWidget(menu_bar)

        tools_row = QHBoxLayout()
        tools_row.addWidget(QLabel("Tools"))
        menu_and_widget_row.addLayout(tools_row)

        main_layout.addLayout(menu_and_widget_row)

        #  创建控制栏行布局
        control_row = QHBoxLayout()
        control_bar = QToolBar()
        control_bar.addWidget(QLabel("Control Bar"))
        control_row.addWidget(control_bar)

        control_row_right = QHBoxLayout()
        control_row_right.addWidget(QLabel("Control Row Right"))
        control_row.addLayout(control_row_right)

        main_layout.addLayout(control_row)

        #  创建播放列表行布局
        playlist_row = QHBoxLayout()
        playlist_select = QComboBox()
        playlist_select.addItem("Playlist Select")
        playlist_row.addWidget(playlist_select)

        playlist = QHBoxLayout()
        playlist.addWidget(QLabel("Playlist"))
        playlist_row.addLayout(playlist)

        main_layout.addLayout(playlist_row)

        #  创建信息和音量行布局
        info_and_volume_row = QHBoxLayout()
        info_and_volume_row.addWidget(QLabel("Info and Volume"))
        main_layout.addLayout(info_and_volume_row)

        #  创建一个中心的 QWidget  来包含主布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle("PySide6 Example")
        self.show()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec()