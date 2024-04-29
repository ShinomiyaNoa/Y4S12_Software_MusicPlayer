from PySide6.QtWidgets import QInputDialog, QListWidget, QMainWindow, QWidget
from PySide6.QtWidgets import QApplication, QSlider, QPushButton
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt, QTimer
from core.AudioCore import AudioPlayer
import sys
import json
import os

class MainWindow(QMainWindow):

    def __init__(self, master=None):
        super().__init__(flags=Qt.FramelessWindowHint)
        self.baseDir = os.path.dirname(os.path.abspath(__file__))
        self.setWindowTitle("Audio Player")

        self.current_playlist_filename = ""

        self.load_qss()

        self.audio_player = AudioPlayer()
        self.create_ui()

        # 加载播放列表
        self.load_existing_playlists()
        self.load_last_opened_playlist()

    def create_ui(self):
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.hbuttonbox = QHBoxLayout()
        self.create_control_buttons()
        self.create_volume_slider()
        self.create_position_slider()
        self.create_add_playlist_button()
        self.create_playlist_widget()
        self.create_playlist_selector()
        self.create_add_file_button()
        self.create_add_folder_button()

        self.widget.setLayout(self.hbuttonbox)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start()

# region Interface creation
    def create_control_buttons(self):
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.hbuttonbox.addWidget(self.play_button)
        self.stopbutton = QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.audio_player.stop)

    def create_volume_slider(self):
        self.hbuttonbox.addStretch(1)
        self.volumeslider = QSlider(Qt.Orientation.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.audio_player.get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.audio_player.set_volume)

    def create_position_slider(self):
        self.positionslider = QSlider(Qt.Orientation.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.setValue(self.audio_player.get_position())
        self.positionslider.sliderMoved.connect(self.audio_player.set_position)
        self.hbuttonbox.addWidget(self.positionslider)

    def create_add_playlist_button(self):
        self.add_playlist_button = QPushButton("Add Playlist", self)
        self.add_playlist_button.clicked.connect(self.add_new_playlist)
        self.hbuttonbox.addWidget(self.add_playlist_button)

    def create_playlist_widget(self):
        self.playlist_widget = QListWidget(self)
        self.hbuttonbox.addWidget(self.playlist_widget)
        self.playlist_widget.itemDoubleClicked.connect(self.play_audio)

    def create_playlist_selector(self):
        self.playlist_selector = QListWidget(self)
        self.hbuttonbox.addWidget(self.playlist_selector)
        self.playlist_selector.itemDoubleClicked.connect(self.load_selected_playlist)

    def create_add_file_button(self):
        self.add_files_button = QPushButton("Add File")
        self.hbuttonbox.addWidget(self.add_files_button)
        self.add_files_button.clicked.connect(self.select_file)

    def create_add_folder_button(self):
        self.add_files_button = QPushButton("Add Folder")
        self.hbuttonbox.addWidget(self.add_files_button)
        self.add_files_button.clicked.connect(self.select_folder)

    def load_qss(self):
        qss_path = os.path.join(self.baseDir, 'style.qss')
        with open(qss_path, 'r', encoding='utf-8') as f:
            qss = f.read()
        self.setStyleSheet(qss)
# endregion

# region Interface refresh
    def closeEvent(self, event):
        if self.audio_player.is_playing():
            self.audio_player.play_pause()
        # 保存当前打开的播放列表的文件名
        playlists_dir = os.path.join(self.baseDir, 'playlists')
        last_opened_playlist_path = os.path.join(playlists_dir, "lastOpenedPlaylist.txt")
        with open(last_opened_playlist_path, 'w', encoding='utf-8') as f:
            f.write(self.current_playlist_filename)

        # 调用父类的closeEvent方法以确保窗口正确关闭
        super().closeEvent(event)

    def update_ui(self):
        self.volumeslider.setValue(self.audio_player.get_volume())
        self.positionslider.setValue(self.audio_player.get_position())

    def update_progress(self):
        position = self.audio_player.get_position()
        self.positionslider.setValue(position)
# endregion

# region Aduio playback
    def play_audio(self, item):
        file_name = item.text()
        # 读取JSON文件获取歌曲地址
        playlists_dir = os.path.join(self.baseDir, 'playlists')
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

    def toggle_play_pause(self):
        if self.audio_player.is_playing():
            self.audio_player.play_pause()
            self.play_button.setText("Play")
        else:
            self.audio_player.play_pause()
            self.play_button.setText("Pause")
# endregion

# region Playlists
    def load_last_opened_playlist(self):
        playlists_dir = os.path.join(self.baseDir, 'playlists')
        last_opened_playlist_path = os.path.join(playlists_dir, "lastOpenedPlaylist.txt")
        if os.path.exists(last_opened_playlist_path):
            with open(last_opened_playlist_path, 'r', encoding='utf-8') as f:
                last_opened_playlist_filename = f.read().strip()
                self.current_playlist_filename=last_opened_playlist_filename
            self.load_playlist(last_opened_playlist_filename)

    def load_existing_playlists(self):
        playlists_dir = os.path.join(self.baseDir, 'playlists')
        playlist_files = [f for f in os.listdir(playlists_dir) if f.endswith('.json')]
        self.playlist_selector.clear()
        self.playlist_selector.addItems(playlist_files)

    def load_selected_playlist(self, item):
        if item is not None:
            playlist_name = item.text()
            self.load_playlist(f"{playlist_name}")

            self.current_playlist_filename = playlist_name

    def update_playlist_selector(self):
        playlists_dir = os.path.join(self.baseDir, 'playlists')
        playlist_files = [f for f in os.listdir(playlists_dir) if f.endswith('.json')]
        self.playlist_selector.clear()
        self.playlist_selector.addItems(playlist_files)

    def load_playlist(self, filename):
        playlists_dir = os.path.join(self.baseDir, 'playlists')
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
        playlists_dir = os.path.join(self.baseDir, 'playlists')
        playlist_json_path = os.path.join(playlists_dir, filename)
        with open(playlist_json_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, ensure_ascii=False, indent=4)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            # 遍历文件夹中的所有文件，并添加到播放列表中
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(('.mp3', '.wav', '.flac')): # 根据需要添加更多文件类型
                        file_path = os.path.join(root, file)
                        self.add_to_playlist(file_path, file)
            # 保存当前播放列表到JSON文件
            self.save_current_playlist_to_json()

    def select_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Audio Files (*.mp3 *.wav *.flac)")
        if file_paths:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                self.add_to_playlist(file_path, file_name)
            # 保存当前播放列表到JSON文件
            self.save_current_playlist_to_json()

    def save_current_playlist_to_json(self):
        # 获取当前播放列表的内容
        playlist_info = []
        for i in range(self.playlist_widget.count()):
            item = self.playlist_widget.item(i)
            if item:
                song_info = {"name": item.text(), "path": item.data(Qt.UserRole)}
                playlist_info.append(song_info)

        # 将播放列表内容保存到JSON文件
        playlists_dir = os.path.join(self.baseDir, 'playlists')
        # 检查文件名是否已经包含了.json扩展名，如果没有，则添加
        if not self.current_playlist_filename.endswith('.json'):
            self.current_playlist_filename += '.json'
        current_playlist_json_path = os.path.join(playlists_dir, self.current_playlist_filename)
        with open(current_playlist_json_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, ensure_ascii=False, indent=4)

    def add_to_playlist(self, file_path, file_name):
        # 将文件添加到播放列表中
        playlists_dir = os.path.join(self.baseDir, 'playlists')
        playlist_json_path = os.path.join(playlists_dir, "playList.json")
        with open(playlist_json_path, 'r', encoding='utf-8') as f:
            playlist_info = json.load(f)
        playlist_info.append(
            {"name": file_name, 
             "path": file_path,
             "bpm":"",
             "spectral_bandwidth":"",
             "spectral_contrast":"",
             "wave_20per_to_30per":""}
            )
        with open(playlist_json_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, ensure_ascii=False, indent=4)
        # 更新UI以反映新添加的文件
        self.playlist_widget.addItem(file_name)

    def add_new_playlist(self):
        # 弹出对话框让用户输入新播放列表的文件名
        playlist_name, ok = QInputDialog.getText(self, "Add Playlist", "Enter playlist name:")
        if ok and playlist_name:
            # 确保文件名有 .json 扩展名
            if not playlist_name.endswith('.json'):
                playlist_name += '.json'
            
            # 创建新的空白 JSON 文件
            playlists_dir = os.path.join(self.baseDir, 'playlists')
            playlist_json_path = os.path.join(playlists_dir, playlist_name)
            try:
                with open(playlist_json_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                # 更新播放列表选择器
                self.update_playlist_selector()
                QMessageBox.information(self, "Success", f"Playlist '{playlist_name}' added successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add playlist: {e}")
# endregion

# region Main
def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
# endregion