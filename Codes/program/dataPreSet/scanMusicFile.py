# scanMusicFile.py

import os
import librosa
import pandas as pd

def scan_music_file(mPath):
    # 创建一个空的DataFrame
    data = pd.DataFrame(columns=['filename', 'spectral_centroids', 'spectral_bandwidth',
                        'spectral_contrast', 'spectral_rolloff', 'spectral_flatness', 'bpm'])

    # 遍历音乐文件夹
    for filename in os.listdir(mPath):
        if filename.endswith('.mp3') or filename.endswith('.wav') or filename.endswith('.flac') or filename.endswith('.dsf'):
            # 加载音乐文件
            y, sr = librosa.load(os.path.join(mPath, filename))

            # 提取频谱特征
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            # 提取BPM
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            # 将特征添加到DataFrame中
            data = data.append({
                'filename': filename,
                'spectral_bandwidth': spectral_bandwidth.mean(),
                'spectral_contrast': spectral_contrast.mean(),
                'bpm': tempo
            }, ignore_index=True)

    # 导出为CSV文件
    data.to_csv('logs/datasetsInformation.csv', index=False)
    return data