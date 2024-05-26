import vlc
import numpy as np
class AudioCore:

    def __init__(self, musicPlayer):
        self.instance = vlc.Instance()
        self.musicPlayer = musicPlayer

        self.media = None

        self.mediaplayer = self.instance.media_player_new()

        self.is_paused = False

        self.target_loudness = -12
        self.volume_adjustment = 1

    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.is_paused = True
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return
            self.mediaplayer.play()
            self.is_paused = False

    def stop(self):
        self.mediaplayer.stop()

    def open_file(self, filepath, loudness):
        self.media = self.instance.media_new(filepath)
        self.mediaplayer.set_media(self.media)

        self.media.parse()
        if loudness is not None:
            # 统一响度到 self.target_loudness
            self.volume_adjustment = self.calculate_volume_adjustment(loudness, self.target_loudness)
            self.set_volume(self.musicPlayer.volumeslider.value())
        self.play_pause()

    def calculate_volume_adjustment(self, current_loudness, target_loudness):
        rms_db = 20*np.log10(current_loudness)
        adjustment_factor = np.power(10, (target_loudness - rms_db) / 20)
        return adjustment_factor

    def set_volume(self, volume):
        target_volume = volume * self.volume_adjustment
        self.mediaplayer.audio_set_volume(int(target_volume))
        print(target_volume)

    def set_position(self, position):
        pos = position / 1000.0
        self.mediaplayer.set_position(pos)

    def get_volume(self):
        return self.mediaplayer.audio_get_volume()

    def get_position(self):
        return self.mediaplayer.get_position() * 1000

    def is_playing(self):
        return self.mediaplayer.is_playing()

    def update_ui(self):
        if not self.mediaplayer.is_playing():
            if not self.is_paused:
                self.stop()