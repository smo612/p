import pandas as pd
from textblob import TextBlob
import os
import logging

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def clean_headlines(df):
    """
    清理新聞標題，去除多餘空格和符號
    """
    logging.info("正在清理新聞標題...")
    df["Headline"] = df["Headline"].str.strip()  # 去除首尾空格
    df["Headline"] = df["Headline"].str.replace(r"[^a-zA-Z0-9\s.,!?']", "", regex=True)  # 去除特殊字符
    return df

def analyze_sentiment(df):
    """
    使用 TextBlob 進行情感分析，添加情感分數
    """
    logging.info("正在進行情感分析...")
    sentiments = []
    for headline in df["Headline"]:
        blob = TextBlob(headline)
        sentiments.append(blob.sentiment.polarity)  # 極性分數 (-1 到 1)
    df["Sentiment"] = sentiments
    return df

def save_results(df, output_path="results/news_with_sentiment.csv"):
    """
    保存結果為新的 CSV 文件
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logging.info(f"結果已保存到 {output_path}")

if __name__ == "__main__":
    # 讀取現有的 CSV 文件
    input_file = "results/news_data.csv"  # 你的 CSV 文件路徑
    if not os.path.exists(input_file):
        logging.error(f"未找到 CSV 文件: {input_file}")
        exit()

    logging.info("正在讀取 CSV 文件...")
    news_df = pd.read_csv(input_file)

    # 清理標題
    news_df = clean_headlines(news_df)

    # 執行情感分析
    news_df = analyze_sentiment(news_df)

    # 保存結果
    save_results(news_df)

    logging.info("情感分析完成！")