import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv('D:\Code\Y4S12Software\logs\savedData\datasetsInformation_entropy_std_dev.csv')

# 设定的标准值
standard_values = [1, 100, 1, 1, 100]

# 定义权值
weightFunc = [0.6, 0.1, 0.2, 0.15, 0.05]

# 计算余弦相似度的列是 'spectral_bandwidth', 'spectral_contrast', 'bpm', 'wav_entropy', 'wav_std_dev'
# 选择这些列进行计算
selected_columns = df[['spectral_bandwidth', 'spectral_contrast', 'bpm', 'wav_entropy', 'wav_std_dev']]

# 对数据进行缩放到(1, 100)
scaler = MinMaxScaler(feature_range=(1, 100))
scaled_columns = scaler.fit_transform(selected_columns)

# 计算加权余弦相似度
weighted_columns = scaled_columns * weightFunc

similarity_scores = cosine_similarity(weighted_columns, [standard_values])

# 将加权余弦相似度添加到数据框中
df['weighted_cosine_similarity'] = similarity_scores.flatten()

# 根据加权余弦相似度对数据进行排序
sorted_indices = df['weighted_cosine_similarity'].argsort()[::-1] # 降序排序

# 根据排序后的索引对原始数据框进行排序
sorted_df = df.iloc[sorted_indices]

# 将排序后的数据写入新的CSV文件
sorted_df.to_csv('logs/sorted_data.csv', index=False)