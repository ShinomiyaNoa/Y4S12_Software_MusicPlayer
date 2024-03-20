# mainTest.py

from PySide6.QtWidgets import QListWidget, QVBoxLayout, QMainWindow, QWidget
from PySide6.QtWidgets import QVBoxLayout, QApplication, QSlider, QPushButton
from PySide6.QtWidgets import QFileDialog, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from core.AudioCore import AudioPlayer
import sys
import json
import os

class MainWindow(QMainWindow):

    def __init__(self, master=None):
        super().__init__(master)
        self.setWindowTitle("Audio Player")

        self.load_qss()

        self.audio_player = AudioPlayer()
        self.create_ui()

        # 加载播放列表
        self.load_playlist("lastList.json")

    def create_ui(self):
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.hbuttonbox = QHBoxLayout()
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.hbuttonbox.addWidget(self.play_button)
        self.stopbutton = QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.audio_player.stop)

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
        self.timer.timeout.connect(self.update_progress)
        self.timer.start()

        # 添加播放列表
        self.playlist_widget = QListWidget(self)
        self.hbuttonbox.addWidget(self.playlist_widget)
        # 双击信号到播放音频
        self.playlist_widget.itemDoubleClicked.connect(self.play_audio)

        self.select_playlist_button = QPushButton("Select Playlist")
        self.hbuttonbox.addWidget(self.select_playlist_button)
        self.select_playlist_button.clicked.connect(self.select_playlist)

    def load_qss(self):
        qss_path = os.path.join(os.path.dirname(__file__), 'style.qss')
        with open(qss_path, 'r', encoding='utf-8') as f:
            qss = f.read()
        self.setStyleSheet(qss)

    def select_file(self):
        dialog_txt = "Choose Audio File"
        filename, _ = QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        if not filename:
            return
        self.audio_player.open_file(filename)

    def update_ui(self):
        self.volumeslider.setValue(self.audio_player.get_volume())
        self.positionslider.setValue(self.audio_player.get_position())

    def update_progress(self):
        position = self.audio_player.get_position()
        self.positionslider.setValue(position)

    def select_playlist(self):
        dialog_txt = "Choose Playlist Folder"
        folder_path = QFileDialog.getExistingDirectory(self, dialog_txt, os.path.expanduser('~'))
        if not folder_path:
            return
        # 清空播放列表
        self.playlist_widget.clear()
        # 添加文件到播放列表
        playlist_info = []
        for filename in os.listdir(folder_path):
            if filename.endswith(('.mp3', '.wav', '.flac')): 
                self.playlist_widget.addItem(filename)
                playlist_info.append({"name": filename, "path": os.path.join(folder_path, filename)})
        # 创建JSON文件来存储播放列表信息
        # 修改为在程序的目录的playlists子目录下创建JSON文件
        playlists_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playlists')
        os.makedirs(playlists_dir, exist_ok=True) # 确保playlists目录存在
        playlist_json_path = os.path.join(playlists_dir, "playList.json")
        with open(playlist_json_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, ensure_ascii=False, indent=4)
        # 创建JSON文件来存储播放列表信息
        playlist_json_path = os.path.join(playlists_dir, "playList.json")
        with open(playlist_json_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, ensure_ascii=False, indent=4)
        # 保存当前的播放列表到lastList.json
        self.save_playlist("lastList.json", playlist_info)

    def play_audio(self, item):
        file_name = item.text()
        # 读取JSON文件来获取歌曲的地址
        playlists_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playlists')
        playlist_json_path = os.path.join(playlists_dir, "playList.json")
        with open(playlist_json_path, 'r', encoding='utf-8') as f:
            playlist_info = json.load(f)
        for song_info in playlist_info:
            if song_info["name"] == file_name:
                file_path = song_info["path"]
                break
        else:
            print(f"Song {file_name} not found in playlist.")
            return
        self.audio_player.open_file(file_path)
        self.audio_player.play_pause()
        self.toggle_play_pause()

    def load_playlist(self, filename):
        playlists_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playlists')
        playlist_json_path = os.path.join(playlists_dir, filename)
        if os.path.exists(playlist_json_path):
            with open(playlist_json_path, 'r', encoding='utf-8') as f:
                playlist_info = json.load(f)
            self.playlist_widget.clear()
            for song_info in playlist_info:
                self.playlist_widget.addItem(song_info["name"])
        else:
            print(f"Playlist file {filename} not found.")

    def save_playlist(self, filename, playlist_info):
        playlists_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playlists')
        playlist_json_path = os.path.join(playlists_dir, filename)
        with open(playlist_json_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, ensure_ascii=False, indent=4)

    def toggle_play_pause(self):
        if self.audio_player.is_playing():
            # 如果正在播放，则暂停播放
            self.audio_player.play_pause()
            self.play_button.setText("Play")
        else:
            # 如果正在暂停，则恢复播放
            self.audio_player.play_pause()
            self.play_button.setText("Pause")


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()