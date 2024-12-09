import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from textblob import TextBlob  # 添加此行修正 NameError 問題

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 清理新聞標題函數
def clean_headlines(df):
    logging.info("正在清理新聞標題...")
    df["Headline"] = df["Headline"].str.strip()
    df["Headline"] = df["Headline"].str.replace(r"[^a-zA-Z0-9\s.,!?']", "", regex=True)
    return df

# 情感分析函數
def analyze_sentiment(df):
    logging.info("正在進行情感分析...")
    sentiments = []
    for headline in df["Headline"]:
        blob = TextBlob(headline)
        sentiments.append(blob.sentiment.polarity)
    df["Sentiment"] = sentiments
    return df



# 可視化按 3 小時分組的情感趨勢
def visualize_sentiment_by_3_hour(df, output_path="results/3_hourly_sentiment_trend.png"):
    """
    將情感分數按 3 小時分組並進行可視化
    """
    logging.info("正在進行 3 小時分組...")
    df["Time"] = pd.to_datetime(df["Time"])
    df["3_Hour_Group"] = df["Time"].dt.floor("3H")  # 按 3 小時分組
    grouped_df = df.groupby(["Ticker", "3_Hour_Group"])["Sentiment"].mean().reset_index()

    logging.info("繪製 3 小時情感趨勢圖...")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=grouped_df, x="3_Hour_Group", y="Sentiment", hue="Ticker", marker="o")
    plt.title("3-Hourly Sentiment Trend", fontsize=16)
    plt.xlabel("3-Hour Time Group", fontsize=12)
    plt.ylabel("Average Sentiment", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(visible=True, linestyle='--', linewidth=0.5)
    plt.legend(title="Ticker")
    plt.tight_layout()

    # 保存圖表
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.show()
    logging.info(f"3 小時情感趨勢圖已保存為 {output_path}")

# 保存結果函數
def save_results(df, output_path="results/news_with_sentiment.csv"):
    """
    保存結果為新的 CSV 文件
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logging.info(f"結果已保存到 {output_path}")

# 主程式
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

    # 可視化按 3 小時分組的情感趨勢
    visualize_sentiment_by_3_hour(news_df)

    logging.info("分析完成！")