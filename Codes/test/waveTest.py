import librosa
import numpy as np

class WaveAnalyzer:
    def __init__(self, filename):
        self.filename = filename
        self.y, self.sr = librosa.load(filename)
        self.audio_length = len(self.y) / self.sr
        # 长度 0->1
        self.start_time = self.audio_length * 0
        self.end_time = self.audio_length * 1
        self.y_segment = self.y[int(self.start_time * self.sr):
                                int(self.end_time * self.sr)]
        self.S = librosa.feature.melspectrogram(y=self.y_segment, 
                                                sr=self.sr, n_mels=128)
        self.log_S = librosa.amplitude_to_db(self.S, ref=np.max)

    # def mean(self):
    #     return np.mean(self.log_S)

    # def median(self):
    #     return np.median(self.log_S)

    # def std_dev(self):
    #     return np.std(self.log_S)

    def entropy(self):
        # 计算熵
        log_S_normalized = self.log_S / np.sum(self.log_S)
        # 添加一个非常小的常数到每个概率值中，避免零概率的情况
        epsilon = 1e-10
        log_S_normalized_smoothed = (log_S_normalized + epsilon) / (np.sum(log_S_normalized) + epsilon * log_S_normalized.shape[0])
        entropy = -np.sum(log_S_normalized_smoothed * np.log2(log_S_normalized_smoothed))
        return entropy

    def std_dev(self):
        # 计算标准差
        std_dev = np.std(self.log_S)
        return std_dev

# if __name__ == "__main__":
#     filename = 'D:/Code/Y4S12Software/Codes/test/【エイプリルフールver.】エイリアンエイリアン ⧸ ニコニコ☆食べもの探し.flac'
#     analyzer = AudioAnalyzer(filename)
#     print("log_S的平均值:", analyzer.mean())
#     print("log_S的中位数:", analyzer.median())
#     print("log_S的标准差:", analyzer.std_dev())