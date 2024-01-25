import vlc

class AudioPlayer:

    def __init__(self):
        # Create a basic vlc instance
        self.instance = vlc.Instance()

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.is_paused = False

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

    def open_file(self, filename):
        self.media = self.instance.media_new(filename)
        self.mediaplayer.set_media(self.media)

        self.media.parse()

        self.play_pause()

    def set_volume(self, volume):
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self, position):
        pos = position / 1000.0
        self.mediaplayer.set_position(pos)

    def get_volume(self):
        return self.mediaplayer.audio_get_volume()

    def get_position(self):
        return self.mediaplayer.get_position() * 1000

    def update_ui(self):
        if not self.mediaplayer.is_playing():
            if not self.is_paused:
                self.stop()