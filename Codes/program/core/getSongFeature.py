import os
import librosa
import pandas as pd
import numpy as np
from core.waveAnalyzer import WaveAnalyzer

def get_song_features(file_path):
    y, sr = librosa.load(file_path)

    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    wave_analyzer = WaveAnalyzer(file_path)
    wav_entropy = wave_analyzer.entropy()
    wav_std_dev = wave_analyzer.std_dev()

    loudness_frames = librosa.feature.rms(y=y)

    return {
        'spectral_bandwidth': spectral_bandwidth.mean(),
        'spectral_contrast': spectral_contrast.mean(),
        'bpm': tempo,
        'wav_entropy': wav_entropy,
        'wav_std_dev': wav_std_dev,
        'loudness': np.max(loudness_frames)
    }