import os
import librosa
import pandas as pd


def get_feature(mPath):
    # 创建一个空的DataFrame
    data = pd.DataFrame(columns=['filename', 'spectral_centroids', 'spectral_bandwidth',
                        'spectral_contrast', 'spectral_rolloff', 'spectral_flatness', 'bpm'])
    i = 0
    # 遍历音乐文件夹
    for filename in os.listdir(mPath):
        if filename.endswith('.mp3') or filename.endswith('.wav') or filename.endswith('.flac') or filename.endswith('.dsf'):
            # 加载音乐文件
            y, sr = librosa.load(os.path.join(
                mPath, filename))

            # 提取频谱特征
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            spectral_flatness = librosa.feature.spectral_flatness(y=y)

            # 提取BPM
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            # 将特征添加到DataFrame中
            data = pd.concat([data, pd.DataFrame({
                'filename': [filename],
                'spectral_centroids': [spectral_centroids.mean()],
                'spectral_bandwidth': [spectral_bandwidth.mean()],
                'spectral_contrast': [spectral_contrast.mean()],
                'spectral_rolloff': [spectral_rolloff.mean()],
                'spectral_flatness': [spectral_flatness.mean()],
                'bpm': [tempo]
            })], ignore_index=True)

    # 导出为CSV文件
    data.to_csv('logs/datasetsInformation.csv', index=False)
    return data
