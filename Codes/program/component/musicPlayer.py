from PySide6.QtWidgets import QInputDialog, QListWidget, QMainWindow, QWidget
from PySide6.QtWidgets import QApplication, QSlider, QPushButton, QRadioButton
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QVBoxLayout
from PySide6.QtWidgets import QButtonGroup, QSplitter, QMenu, QLabel
from PySide6.QtCore import Qt, QTimer
from core.AudioCore import AudioCore
from core.getSongFeature import get_song_features
from core.cosineSimilarity import calculate_weighted_cosine_similarity
import pandas as pd
import numpy as np
import threading
import librosa
import sys
import json
import os
import random

class MusicPlayer(QWidget):
    def __init__(self, parent=None, mainWindow=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        
        self.current_playlist_filename = ""
        self.playback_mode = 'sequential'
        self.last_five_tracks = []

        self.ranges = {
            'spectral_bandwidth': (900,3100),
            'spectral_contrast': (18.5,27.5),
            'bpm': (60,240),
            'wav_entropy': (0.045,0.054),
            'wav_std_dev': (9,17.5)
        }
        self.setAutoFillBackground(True)

        # 加载 QSS 文件
        self.load_qss("component\\qss\\musicPlayer.qss")

        self.audio_player = AudioCore(self)
        self.create_ui()

        # 加载播放列表
        self.load_existing_playlists()
        self.load_last_opened_playlist()

        # # 播放次数计时器
        # self.play_count_timer = QTimer(self)
        # self.play_count_timer.setInterval(10000)
        # self.play_count_timer.timeout.connect(self.update_play_count)

        # 在播放器打开时扫描并更新 cosine similarity list
        threading.Thread(target=self.scan_and_update_cosine_similarity_list).start()

    def create_ui(self):
        self.widget = QVBoxLayout(self)

        self.main_box = QVBoxLayout()

        self.headline_box = QHBoxLayout()
        self.create_add_file_button()
        self.create_add_folder_button()
        self.create_add_playlist_button()
        self.create_style_switch_button()

        self.splitter = QSplitter(Qt.Horizontal)
        self.playlist_box = QHBoxLayout()
        self.create_playlist_selector()
        self.create_playlist_widget()
        self.playlist_box.addWidget(self.splitter)

        self.splitter.setSizes([int(0.2 * 700), int(0.8 * 700)])

        self.control_box = QHBoxLayout()
        self.create_control_buttons()
        self.create_playback_control_buttons()
        self.create_volume_slider()
        self.create_position_slider()

        self.main_box.addLayout(self.headline_box)
        self.main_box.addLayout(self.playlist_box)
        self.main_box.addLayout(self.control_box)

        self.widget.addLayout(self.main_box)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start()

# region Interface creation
    def create_style_switch_button(self):
        self.style_switch_button = QPushButton("Switch Style", self)
        self.style_switch_button.clicked.connect(self.switch_style)
        self.headline_box.addWidget(self.style_switch_button) 

    def create_control_buttons(self):
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.control_box.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.control_box.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.audio_player.stop)

    def create_playback_control_buttons(self):
        self.previous_button = QPushButton("Previous", self)
        self.previous_button.clicked.connect(self.play_previous)
        self.control_box.addWidget(self.previous_button)

        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.play_next)
        self.control_box.addWidget(self.next_button)

        self.playback_mode_button = QPushButton("Sequential", self)
        self.playback_mode_button.clicked.connect(self.toggle_playback_mode)
        self.control_box.addWidget(self.playback_mode_button)

    def create_volume_slider(self):
        self.control_box.addStretch(1)
        self.volumeslider = QSlider(Qt.Orientation.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.audio_player.get_volume())
        self.volumeslider.setToolTip("Volume")
        self.control_box.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.audio_player.set_volume)

    def create_position_slider(self):
        self.positionslider = QSlider(Qt.Orientation.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.setValue(self.audio_player.get_position())
        self.positionslider.sliderMoved.connect(self.audio_player.set_position)
        self.control_box.addWidget(self.positionslider)

    def create_add_playlist_button(self):
        self.add_playlist_button = QPushButton("New Playlist", self)
        self.add_playlist_button.clicked.connect(self.add_new_playlist)
        self.headline_box.addWidget(self.add_playlist_button)
        self.headline_box.addStretch(1)

    def create_equalizer_settings_button(self):
        equalizerSettingsButton = QPushButton("Equalizer Settings", self)
        equalizerSettingsButton.clicked.connect(self.open_equalizer_settings_dialog)

    def create_playlist_widget(self):
        self.playlist_widget = QListWidget(self)
        self.splitter.addWidget(self.playlist_widget)
        self.playlist_widget.itemDoubleClicked.connect(self.play_audio)
        self.playlist_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlist_widget.customContextMenuRequested.connect(self.show_context_menu)

    def create_playlist_selector(self):
        self.playlist_selector = QListWidget(self)
        self.splitter.addWidget(self.playlist_selector)
        self.playlist_selector.itemDoubleClicked.connect(self.load_selected_playlist)
        self.playlist_selector.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlist_selector.customContextMenuRequested.connect(self.show_context_menu)

    def create_add_file_button(self):
        self.add_files_button = QPushButton("Add File")
        self.headline_box.addWidget(self.add_files_button)
        self.add_files_button.clicked.connect(self.select_file)

    def create_add_folder_button(self):
        self.add_folder_button = QPushButton("Add Folder")
        self.headline_box.addWidget(self.add_folder_button)
        self.add_folder_button.clicked.connect(self.select_folder)

    def load_qss(self, qss_file):
        qss_path = os.path.join(self.mainWindow.baseDir, qss_file)
        with open(qss_path, "r") as f:
            self.setStyleSheet(f.read())
# endregion

# region Interface refresh
    def closeEvent(self, event):
        if self.audio_player.is_playing():
            self.audio_player.play_pause()
        # 保存当前打开的播放列表的文件名
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
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

    def show_context_menu(self, position):
        sender = self.sender()
        item = sender.itemAt(position)
        if item:
            menu = QMenu()
            # Directly add a menu item without using QAction
            menu.addAction("Delete", lambda: self.delete_item(sender, item))
            menu.exec(sender.mapToGlobal(position))

    def switch_style(self):
        styles = ["musicPlayer", "brown", "black", "green", "white"] # List of available styles
        style, ok = QInputDialog.getItem(self, "Select Style", "Style:", styles, 0, False)
        if ok and style:
            qss_path = os.path.join(self.mainWindow.baseDir, f"component\\qss\\{style}.qss")
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())

    def open_equalizer_settings_dialog(self):
        # 添加一个功能，打开均衡器设置对话框
        equalizer_settings_dialog = QLabel(self)
        equalizer_settings_dialog.setWindowTitle("Equalizer Settings")
        equalizer_layout = QVBoxLayout()
        equalizer_settings_dialog.setLayout(equalizer_layout)

        equalizer_label = QLabel("Adjust Equalizer Settings:")
        equalizer_layout.addWidget(equalizer_label)

        equalizer_slider = QSlider(Qt.Horizontal)
        equalizer_slider.setMinimum(-10)
        equalizer_slider.setMaximum(10)
        equalizer_slider.setValue(0)
        equalizer_slider.setTickPosition(QSlider.TicksBelow)
        equalizer_layout.addWidget(equalizer_slider)

        save_button = QPushButton("Save")
        equalizer_layout.addWidget(save_button)

        equalizer_settings_dialog.exec()
# endregion

# region Aduio playback
    def play_audio(self, item):
        file_name = item.text()
        # 读取JSON文件获取歌曲地址
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        playlist_json_path = os.path.join(playlists_dir, self.current_playlist_filename)
        with open(playlist_json_path, 'r', encoding='utf-8') as f:
            playlist_info = json.load(f)
        for song_info in playlist_info:
            if song_info["name"] == file_name:
                file_path = song_info["path"]
                break
        else:
            print(f"Song {file_name} not found in playlist.")
            return
        self.audio_player.open_file(file_path, song_info['loudness'])

        # # 计时器在播放后开始准备计数
        # self.play_count_timer.start()

    def toggle_play_pause(self):
        if self.audio_player.is_playing():
            self.audio_player.play_pause()
            self.play_button.setText("Play")
        else:
            self.audio_player.play_pause()
            self.play_button.setText("Pause")

    def toggle_playback_mode(self):
        if self.playback_mode == 'sequential':
            self.playback_mode = 'random'
            self.playback_mode_button.setText("Random")
        else:
            self.playback_mode = 'sequential'
            self.playback_mode_button.setText("Sequential")

    def play_next(self):
        if self.playback_mode =='sequential':
            current_index = self.playlist_widget.currentRow()
            next_index = (current_index + 1) % self.playlist_widget.count()
            self.playlist_widget.setCurrentRow(next_index)
            self.play_audio(self.playlist_widget.item(next_index))
        else:
            current_track = self.playlist_widget.currentItem().text()
            self.last_five_tracks.append(current_track)
            if len(self.last_five_tracks) > 5:
                self.last_five_tracks.pop(0)
            random_index = random.randint(0, self.playlist_widget.count() - 1)
            self.playlist_widget.setCurrentRow(random_index)
            self.play_audio(self.playlist_widget.item(random_index))
            

    def play_previous(self):
        if self.playback_mode == 'sequential':
            current_index = self.playlist_widget.currentRow()
            previous_index = (current_index - 1) % self.playlist_widget.count()
            self.playlist_widget.setCurrentRow(previous_index)
            self.play_audio(self.playlist_widget.item(previous_index))
        else:
            if not self.last_five_tracks or len(self.last_five_tracks) > 5:
                self.last_five_tracks.clear()
                random_index = random.randint(0, self.playlist_widget.count() - 1)
                self.playlist_widget.setCurrentRow(random_index)
                self.play_audio(self.playlist_widget.item(random_index))
            else:
                last_track = self.last_five_tracks.pop()
                for i in range(self.playlist_widget.count()):
                    if self.playlist_widget.item(i).text() == last_track:
                        self.playlist_widget.setCurrentRow(i)
                        self.play_audio(self.playlist_widget.item(i))
                        break

    # def update_play_count(self):
    #     # print(f"Play count: {self.play_count_timer.elapsed()}")
    #     current_song_info = self.get_current_song_info()
    #     if current_song_info:
    #         current_song_info["play_count"] += 1
    #         self.save_playlist(self.current_playlist_filename, self.get_playlist_info())

    # def get_current_song_info(self):
    #     current_song_name = self.playlist_widget.currentItem().text()
    #     playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
    #     playlist_json_path = os.path.join(playlists_dir, self.current_playlist_filename)
    #     with open(playlist_json_path, 'r', encoding='utf-8') as f:
    #         playlist_info = json.load(f)
    #     for song_info in playlist_info:
    #         if song_info["name"] == current_song_name:
    #             return song_info
    #     return None

    # def get_playlist_info(self):
    #     playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
    #     playlist_json_path = os.path.join(playlists_dir, self.current_playlist_filename)
    #     with open(playlist_json_path, 'r', encoding='utf-8') as f:
    #         playlist_info = json.load(f)
    #     return playlist_info

    # def save_playlist(self, filename, playlist_info):
    #     playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
    #     playlist_json_path = os.path.join(playlists_dir, filename)
    #     with open(playlist_json_path, 'w', encoding='utf-8') as f:
    #         json.dump(playlist_info, f, ensure_ascii=False, indent=4)
# endregion

# region Playlists
    def load_last_opened_playlist(self):
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        last_opened_playlist_path = os.path.join(playlists_dir, "lastOpenedPlaylist.txt")
        if os.path.exists(last_opened_playlist_path):
            with open(last_opened_playlist_path, 'r', encoding='utf-8') as f:
                last_opened_playlist_filename = f.read().strip()
                self.current_playlist_filename=last_opened_playlist_filename
            self.load_playlist(last_opened_playlist_filename)

    def load_existing_playlists(self):
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        playlist_files = [f for f in os.listdir(playlists_dir) if f.endswith('.json')]
        self.playlist_selector.clear()
        self.playlist_selector.addItems(playlist_files)

    def load_selected_playlist(self, item):
        if item is not None:
            playlist_name = item.text()
            self.load_playlist(f"{playlist_name}")

            self.current_playlist_filename = playlist_name

    def update_playlist_selector(self):
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        playlist_files = [f for f in os.listdir(playlists_dir) if f.endswith('.json')]
        self.playlist_selector.clear()
        self.playlist_selector.addItems(playlist_files)

    def load_playlist(self, filename):
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
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
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        playlist_json_path = os.path.join(playlists_dir, filename)
        with open(playlist_json_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, ensure_ascii=False, indent=4)

    def select_folder(self):
        # 开多线程
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            if not self.mainWindow.thread_stop_flag:
                threading.Thread(target=self.process_folder, args=(folder_path,)).start()

    def process_folder(self, folder_path):
        # 遍历文件夹中的所有文件，并添加到播放列表中
        total_files = sum([len(files) for _, _, files in os.walk(folder_path)])
        processed_files = 0
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.mp3', '.wav', '.flac')): # 根据需要添加更多文件类型
                    file_path = os.path.join(root, file)
                    self.add_to_playlist(file_path, file)
                    processed_files += 1
                    print(f"Processed {processed_files} of {total_files} files.")
        print("Folder processing completed.")

        # 在选择文件夹后扫描并更新 cosine similarity list
        # playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        # cosine_similarity_list_path = os.path.join(playlists_dir, 'cosineSlimilarityList.json')
        # with open(cosine_similarity_list_path, 'r', encoding='utf-8') as f:
        #     cosine_similarity_list = json.load(f)

        threading.Thread(target=self.scan_and_update_cosine_similarity_list).start()

    def select_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Audio Files (*.mp3 *.wav *.flac)")
        if file_paths:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                self.add_to_playlist(file_path, file_name)

        threading.Thread(target=self.scan_and_update_cosine_similarity_list).start()

    def add_to_playlist(self, file_path, file_name):
        # current playlist
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        playlist_json_path = os.path.join(playlists_dir, self.current_playlist_filename)
        with open(playlist_json_path, 'r', encoding='utf-8') as f:
            playlist_info = json.load(f)

        for song in playlist_info:
            if song["path"] == file_path:
                print(f"File {file_name} is already in the playlist.")
                return

        playlist_info.append({
            "name": file_name, 
            "path": file_path,
            "spectral_bandwidth": None,
            "spectral_contrast": None,
            "bpm": None,
            'wav_entropy': None,
            'wav_std_dev': None,
            "loudness": None,
            "play_count": 0,
            "weighted_cosine_similarity": None,
        })

        with open(playlist_json_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, ensure_ascii=False, indent=4)

        self.playlist_widget.addItem(file_name)

        cosine_similarity_list_path = os.path.join(playlists_dir, 'cosineSlimilarityList.json')
        with open(cosine_similarity_list_path, 'r', encoding='utf-8') as f:
            cosine_similarity_list = json.load(f)

        for song in cosine_similarity_list:
            if song["path"] == file_path:
                return

        cosine_similarity_list.append({
            "name": file_name, 
            "path": file_path,
            "spectral_bandwidth": None,
            "spectral_contrast": None,
            "bpm": None,
            'wav_entropy': None,
            'wav_std_dev': None,
            "loudness": None,
            "play_count": 0,
            "weighted_cosine_similarity": None
        })

        with open(cosine_similarity_list_path, 'w', encoding='utf-8') as f:
            json.dump(cosine_similarity_list, f, ensure_ascii=False, indent=4)

    def scan_and_update_cosine_similarity_list(self):
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        cosine_similarity_list_path = os.path.join(playlists_dir, 'cosineSlimilarityList.json')
        with open(cosine_similarity_list_path, 'r', encoding='utf-8') as f:
            cosine_similarity_list = json.load(f)

        updated_songs = []

        for song in cosine_similarity_list:
            if self.mainWindow.thread_stop_flag == False:
                if song["bpm"] is None or song["spectral_bandwidth"] is None or song["spectral_contrast"] is None or song["weighted_cosine_similarity"] is None:
                    print(f"Updating {song['name']}")
                    features = get_song_features(song["path"])
                    features_df = pd.DataFrame(features, index=[0])
                    # 更新歌曲信息
                    song["spectral_bandwidth"] = features['spectral_bandwidth']
                    song["spectral_contrast"] = features['spectral_contrast']
                    song["bpm"] = features['bpm']
                    # 计算加权余弦相似度
                    song["wav_entropy"] = features['wav_entropy']
                    song["wav_std_dev"] = float(features['wav_std_dev'])
                    song["loudness"] = float(features['loudness'])
                    song["weighted_cosine_similarity"] = calculate_weighted_cosine_similarity(features_df, self.ranges)
                    updated_songs.append(song)

                    self.update_loudness_in_other_playlists(song["path"], song["loudness"])

                    with open(cosine_similarity_list_path, 'w', encoding='utf-8') as f:
                        json.dump(cosine_similarity_list, f, ensure_ascii=False, indent=4)
                    self.sort_cosine_similarity_list(cosine_similarity_list_path)
                    self.record_feature_ranges()

    def update_loudness_in_other_playlists(self, song_path, new_loudness):
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        playlist_files = [f for f in os.listdir(playlists_dir) if f.endswith('.json')]
        for playlist_file in playlist_files:
            playlist_path = os.path.join(playlists_dir, playlist_file)
            with open(playlist_path, 'r', encoding='utf-8') as f:
                playlist = json.load(f)
            for song in playlist:
                if song["path"] == song_path:
                    song["loudness"] = new_loudness
            with open(playlist_path, 'w', encoding='utf-8') as f:
                json.dump(playlist, f, ensure_ascii=False, indent=4)


    def record_feature_ranges(self):
        all_features = self.get_all_song_features()
        self.ranges = {
            'spectral_bandwidth': (min(self.ranges['spectral_bandwidth'][0],
                                       min(all_features['spectral_bandwidth'])), 
                                       max(self.ranges['spectral_bandwidth'][1],
                                           max(all_features['spectral_bandwidth']))),
            'spectral_contrast': (min(self.ranges['spectral_contrast'][0],
                                      min(all_features['spectral_contrast'])), 
                                      max(self.ranges['spectral_contrast'][1],
                                          max(all_features['spectral_contrast']))),
            'bpm': (min(self.ranges['bpm'][0],
                         min(all_features['bpm'])), 
                         max(self.ranges['bpm'][1],
                             max(all_features['bpm']))),
            'wav_entropy': (min(self.ranges['wav_entropy'][0],
                                 min(all_features['wav_entropy'])), 
                                 max(self.ranges['wav_entropy'][1],
                                     max(all_features['wav_entropy']))),
            'wav_std_dev': (min(self.ranges['wav_std_dev'][0],
                                 min(all_features['wav_std_dev'])), 
                                 max(self.ranges['wav_std_dev'][1],
                                     max(all_features['wav_std_dev'])))
        }

    def get_all_song_features(self):
        playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
        cosine_similarity_list_path = os.path.join(playlists_dir, 'cosineSlimilarityList.json')
        with open(cosine_similarity_list_path, 'r', encoding='utf-8') as f:
            cosine_similarity_list = json.load(f)
        all_features = []
        for song in cosine_similarity_list:
            if song["spectral_bandwidth"] is None or song["spectral_contrast"] is None or song["bpm"] is None or song["wav_entropy"] is None or song["wav_std_dev"] is None or song["loudness"] is None or song["weighted_cosine_similarity"] is None:
                continue
            all_features.append(song)
        all_features_df = pd.DataFrame(all_features)
        return all_features_df


    def sort_cosine_similarity_list(self, cosine_similarity_list_path):
        with open(cosine_similarity_list_path, 'r', encoding='utf-8') as f:
            cosine_similarity_list = json.load(f)

        # 过滤weighted_cosine_similarity为None
        filtered_list = [item for item in cosine_similarity_list if item['weighted_cosine_similarity'] is not None]
        add_list = [item for item in cosine_similarity_list if item['weighted_cosine_similarity'] is None]

        # 插排
        for i in range(1, len(filtered_list)):
            key = filtered_list[i]
            j = i - 1
            while j >= 0 and filtered_list[j]['weighted_cosine_similarity'] < key['weighted_cosine_similarity']:
                filtered_list[j + 1] = filtered_list[j]
                j -= 1
            filtered_list[j + 1] = key

        # 写回文件
        with open(cosine_similarity_list_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_list+add_list, f, ensure_ascii=False, indent=4)

    def add_new_playlist(self):
        # 弹出对话框让用户输入新播放列表的文件名
        playlist_name, ok = QInputDialog.getText(self, "Add Playlist", "Enter playlist name:")
        if ok and playlist_name:
            # 确保文件名有 .json 扩展名
            if not playlist_name.endswith('.json'):
                playlist_name += '.json'
            
            # 创建新的空白 JSON 文件
            playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists')
            playlist_json_path = os.path.join(playlists_dir, playlist_name)
            try:
                with open(playlist_json_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                # 更新播放列表选择器
                self.update_playlist_selector()
                self.load_playlist(playlist_name)
                QMessageBox.information(self, "Success", f"Playlist '{playlist_name}' added successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add playlist: {e}")

    def delete_item(self, list_widget, item):
        if list_widget == self.playlist_widget:
            # 处理歌曲删除
            song_name = item.text()
            playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists') # Define playlists_dir here
            playlist_json_path = os.path.join(playlists_dir, self.current_playlist_filename)
            with open(playlist_json_path, 'r', encoding='utf-8') as f:
                playlist_info = json.load(f)
            playlist_info = [song for song in playlist_info if song["name"] != song_name]
            with open(playlist_json_path, 'w', encoding='utf-8') as f:
                json.dump(playlist_info, f, ensure_ascii=False, indent=4)
            self.playlist_widget.takeItem(self.playlist_widget.row(item))
            QMessageBox.information(self, "Success", f"Song '{song_name}' has been deleted from the playlist.")
        elif list_widget == self.playlist_selector:
            # 处理播放列表删除
            playlist_name = item.text()
            playlists_dir = os.path.join(self.mainWindow.baseDir, 'playlists') # Define playlists_dir here
            playlist_path = os.path.join(playlists_dir, playlist_name)
            if os.path.exists(playlist_path):
                os.remove(playlist_path)
                self.playlist_selector.takeItem(self.playlist_selector.row(item))
                if self.current_playlist_filename == playlist_name:
                    self.current_playlist_filename = ""
                    self.playlist_widget.clear()
                QMessageBox.information(self, "Success", f"Playlist '{playlist_name}' has been deleted.")
            else:
                QMessageBox.warning(self, "Error", f"Playlist '{playlist_name}' does not exist.")
        else:
            # 如果不是从playlist_widget或playlist_selector删除，则只删除UI中的项
            list_widget.takeItem(list_widget.row(item))
# endregion