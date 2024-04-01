# import os
# import librosa
# import pandas as pd
# from waveTest import WaveAnalyzer

# def get_feature(mPath):
#     # 创建一个空的DataFrame
#     data = pd.DataFrame(columns=['filename', 
#                          'spectral_bandwidth',
#                          'spectral_contrast',
#                          'bpm', 'wav_30_to_40'])
#     i = 0
#     # 遍历音乐文件夹
#     for filename in os.listdir(mPath):
#         if filename.endswith('.mp3') or filename.endswith('.wav') or filename.endswith('.flac') or filename.endswith('.dsf'):
#             # 加载音乐文件
#             y, sr = librosa.load(os.path.join(
#                 mPath, filename))

#             # 提取频谱特征
#             spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
#             spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

#             # 提取BPM
#             tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

#             # Create a WaveAnalyzer instance for the current file
#             wave_analyzer = WaveAnalyzer(os.path.join(mPath, filename))
#             # Calculate the mean value of the segment from 0.3 to 0.4 of the audio file
#             wav_30_to_40_mean = wave_analyzer.mean()

#             # 将特征添加到DataFrame中
#             data = pd.concat([data, pd.DataFrame({
#                 'filename': [filename],
#                 'spectral_bandwidth': [spectral_bandwidth.mean()],
#                 'spectral_contrast': [spectral_contrast.mean()],
#                 'bpm': [tempo],
#                 'wav_30_to_40':[wav_30_to_40_mean]
#             })], ignore_index=True)

#     # 导出为CSV文件
#     data.to_csv('logs/datasetsInformation.csv', index=False)
#     return data

import os
import librosa
import pandas as pd
from waveTest import WaveAnalyzer

def get_feature(mPath):
    # Create an empty DataFrame
    data = pd.DataFrame(columns=['filename', 
                         'spectral_bandwidth',
                         'spectral_contrast',
                         'bpm'])
    # Get the total number of files to process
    total_files = len([f for f in os.listdir(mPath) if f.endswith(('.mp3', '.wav', '.flac', '.dsf'))])
    processed_files = 0

    # Iterate through music files
    for filename in os.listdir(mPath):
        if filename.endswith('.mp3') or filename.endswith('.wav') or filename.endswith('.flac') or filename.endswith('.dsf'):
            # Load the music file
            y, sr = librosa.load(os.path.join(mPath, filename))

            # Extract spectral features
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

            # Extract BPM
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            # Create a WaveAnalyzer instance for the current file
            wave_analyzer = WaveAnalyzer(os.path.join(mPath, filename))
            # Calculate the mean value of the segment from 0.3 to 0.4 of the audio file
            wav_entropy = wave_analyzer.entropy()
            wav_std_dev = wave_analyzer.std_dev()


            # Add features to the DataFrame
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

    # Export to CSV file
    data.to_csv('logs/datasetsInformation.csv', index=False)
    return data

if __name__ == "__main__":
    mPath = 'D:\\Music\\MusicCollection1'
    get_feature(mPath)