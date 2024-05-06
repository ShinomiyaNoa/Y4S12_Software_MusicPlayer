from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

def calculate_weighted_cosine_similarity(features, feature_ranges):
    standard_values = [1, 100, 1, 1, 100]
    weightFunc = [0.6, 0.1, 0.2, 0.15, 0.05]

    print(feature_ranges)

    features_line = features[['spectral_bandwidth', 'spectral_contrast', 'bpm', 'wav_entropy', 'wav_std_dev']]

    for feature, (min_val, max_val) in feature_ranges.items():
        features_line[feature] = (features_line[feature] - min_val) / (max_val - min_val) * 99 + 1

    weighted_features = features_line * weightFunc
    similarity_score = cosine_similarity(weighted_features, [standard_values])
    return similarity_score[0][0]