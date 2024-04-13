import os
import librosa
import pandas as pd
from waveTest import WaveAnalyzer

def get_feature(mPath):
    data = pd.DataFrame(columns=['filename', 
                         'spectral_bandwidth',
                         'spectral_contrast',
                         'bpm'])
    # 进度
    total_files = len([f for f in os.listdir(mPath) if f.endswith(('.mp3', '.wav', '.flac', '.dsf'))])
    processed_files = 0

    # 遍历文件
    for filename in os.listdir(mPath):
        if filename.endswith('.mp3') or filename.endswith('.wav') or filename.endswith('.flac') or filename.endswith('.dsf'):
            y, sr = librosa.load(os.path.join(mPath, filename))

            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            wave_analyzer = WaveAnalyzer(os.path.join(mPath, filename))

            wav_entropy = wave_analyzer.entropy()
            wav_std_dev = wave_analyzer.std_dev()


            data = pd.concat([data, pd.DataFrame({
                'filename': [filename],
                'spectral_bandwidth': [spectral_bandwidth.mean()],
                'spectral_contrast': [spectral_contrast.mean()],
                'bpm': [tempo],
                'wav_entropy': [wav_entropy],
                'wav_std_dev': [wav_std_dev]
            })], ignore_index=True)

            processed_files += 1
            print(f"Processed {processed_files} out of {total_files} files.")

    data.to_csv('logs/datasetsInformation.csv', index=False)
    return data

if __name__ == "__main__":
    mPath = 'D:\\Music\\MusicCollection1'
    get_feature(mPath)