from sklearn.preprocessing import LabelEncoder
from datasketch import MinHash, MinHashLSH
from Codes.test.dataPreSetsTest import get_feature
import pandas as pd

# 导入数据
df = get_feature('D:/Code/Y4S12Software/datasets')

# 使用LabelEncoder将你的标签转换为整数
le = LabelEncoder()
df['label'] = le.fit_transform(df['genre'])

# 创建MinHash对象
minhashes = {}
for idx, row in df.iterrows():
    m = MinHash(num_perm=128)
    for d in row['features']:
        m.update(str(d).encode('utf8'))
    minhashes[idx] = m

# 创建LSH索引
lsh = MinHashLSH(threshold=0.5, num_perm=128)
for idx, minhash in minhashes.items():
    lsh.insert(idx, minhash)

# 对每首歌进行聚类
clusters = {}
for idx in df.index:
    result = lsh.query(minhashes[idx])
    if len(result) > 1:
        clusters[idx] = result

# 创建一个新的DataFrame来存储聚类结果
cluster_df = pd.DataFrame.from_dict(clusters, orient='index')

# 导出聚类结果为CSV文件
cluster_df.to_csv('clusters.csv')
