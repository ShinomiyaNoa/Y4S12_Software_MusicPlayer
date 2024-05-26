import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv('D:\Code\Y4S12Software\logs\datasetsInformation_1_entropy.csv')

standard_values = [1, 10e-10]

weightFunc = [1,10e-10]

selected_columns = df[['spectral_bandwidth', 'bpm']]

scaler = MinMaxScaler(feature_range=(1, 100))
scaled_columns = scaler.fit_transform(selected_columns)

weighted_columns = scaled_columns * weightFunc

# similarity_scores = cosine_similarity(weighted_columns, [standard_values])

# 使用欧几里得距离计算距离
distances = euclidean_distances(weighted_columns, [standard_values])

# 计算相似度，这里我们简单地取倒数作为相似度，因为欧几里得距离越小，表示越接近
similarity_scores = 1 / distances

df['weighted_cosine_similarity'] = similarity_scores.flatten()

sorted_indices = df['weighted_cosine_similarity'].argsort()[::-1]

sorted_df = df.iloc[sorted_indices]

sorted_df.to_csv('logs/output.csv', index=False)