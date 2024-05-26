import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(row1, row2):
    """
    计算两个genre列表之间的相似度。
    使用余弦相似度作为相似度指标。
    """
    # 初始化CountVectorizer
    vectorizer = CountVectorizer().fit([row1, row2])
    
    # 将genre列表转换为词袋模型向量
    vectors = vectorizer.transform([row1, row2]).toarray()
    
    # 计算余弦相似度
    csim = cosine_similarity(vectors[0:1], vectors[1:2])
    
    return csim[0][0]

def process_csv(input_file, output_file):
    # 指定正确的编码（这里使用gbk）
    df = pd.read_csv(input_file, encoding='gbk')
    
    # 创建一个新的DataFrame来存储结果，增加一个'similarity'列
    result_df = pd.DataFrame(columns=['id', 'title', 'genre', 'similarity'])
    
    # 遍历DataFrame中的每一行，但跳过id为11和213的行
    for i in range(1, len(df)):  # 从第三行开始，因为第一行没有上一行，第二行只有上一行
        # 检查当前行的id是否为11或213，如果是则跳过
        if df.loc[i, 'id'] in [11, 12, 13, 14, 213, 214, 215, 216]:
            continue
        
        # 获取当前行和上一行的genre
        current_genre = df.loc[i, 'genre']
        previous_genre = df.loc[i - 3, 'genre'] if i > 1 else None  # 如果是第一行，则没有上一行
        
        # 如果有上一行，则计算它们之间的相似度并添加到结果中
        if previous_genre:
            similarity = calculate_similarity(previous_genre, current_genre)
            # 强调前面的genre
            genre_pair = f"{previous_genre} -> {current_genre}"
            result_row = pd.DataFrame({
                'id': [df.loc[i, 'id']],
                'title': [df.loc[i, 'title']],
                'genre': [genre_pair],
                'similarity': [similarity]
            })
            result_df = pd.concat([result_df, result_row], ignore_index=True)
    
    # 将结果写入新CSV文件
    result_df.to_csv(output_file, index=False)

# 调用函数，将输入文件路径和输出文件路径传递给它
input_file_path = 'file:///d:/Code/Y4S12Software/logs/partInfo/1.csv'
output_file_path = 'logs/前四首全参数+权值+归一化.csv'  # 确保替换为实际的输出文件路径
process_csv(input_file_path, output_file_path)