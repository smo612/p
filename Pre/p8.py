import requests
import os
import shutil
import pandas as pd
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 清空資料夾
def clear_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        logging.info(f"已清空資料夾: {directory}")
    os.makedirs(directory, exist_ok=True)

# 爬取新聞資料
def fetch_stock_data(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    os.makedirs("datasets", exist_ok=True)
    if response.status_code == 200:
        file_name = f"{ticker.lower()}_finviz.html"
        file_path = os.path.join("datasets", file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
        logging.info(f"{ticker.upper()} 的 HTML 已成功保存到 {file_path}")
    else:
        logging.error(f"無法獲取 {ticker.upper()} 資料，HTTP 狀態碼: {response.status_code}")

# 解析 HTML 並提取新聞
def parse_html_to_dataframe(directory="datasets"):
    if not os.path.exists(directory):
        logging.error(f"{directory} 資料夾不存在，請先執行爬取步驟。")
        return None
    parsed_news = []
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        ticker = file_name.split("_")[0].upper()
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
                news_table = soup.find(id="news-table")
                if not news_table:
                    logging.warning(f"未在 {file_name} 中找到 'news-table'，跳過該檔案。")
                    continue
                rows = news_table.findAll("tr")
                for row in rows:
                    if row.a and row.td:
                        headline = row.a.get_text(strip=True)
                        time_text = row.td.get_text(strip=True)
                        parsed_news.append([ticker, time_text, headline])
        except Exception as e:
            logging.error(f"解析 {file_name} 時出現錯誤: {e}")
    news_df = pd.DataFrame(parsed_news, columns=["Ticker", "Time", "Headline"])
    return news_df

# 處理時間欄
def process_time_column(df):
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    def convert_time(time_str):
        if "Today" in time_str:
            time_str = time_str.replace("Today", str(today))
        elif "Yesterday" in time_str:
            time_str = time_str.replace("Yesterday", str(yesterday))
        else:
            if len(time_str.split()) == 1:
                time_str = f"{today} {time_str}"
        for fmt in ("%Y-%m-%d %I:%M%p", "%b-%d-%y %I:%M%p"):
            try:
                return datetime.strptime(time_str, fmt).strftime("%Y/%m/%d %H:%M:%S")
            except ValueError:
                continue
        return None
    df["Time"] = df["Time"].apply(convert_time)
    df.dropna(subset=["Time"], inplace=True)
    return df

# 清理標題並保存數據
def clean_and_save_data(df, output_path="results/news_data.csv"):
    df["Headline"] = df["Headline"].str.strip()
    df.drop_duplicates(subset=["Ticker", "Time", "Headline"], inplace=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logging.info(f"數據已保存到 {output_path}")

# 清理新聞標題
def clean_headlines(df):
    df["Headline"] = df["Headline"].str.replace(r"[^a-zA-Z0-9\s.,!?']", "", regex=True)
    return df

# 情感分析
def analyze_sentiment(df):
    sentiments = [TextBlob(headline).sentiment.polarity for headline in df["Headline"]]
    df["Sentiment"] = sentiments
    return df

# 可視化按 3 小時分組的情感趨勢
def visualize_sentiment_by_3_hour(df, output_path="results/3_hourly_sentiment_trend.png"):
    df["Time"] = pd.to_datetime(df["Time"])
    df["3_Hour_Group"] = df["Time"].dt.floor("3h")
    grouped_df = df.groupby(["Ticker", "3_Hour_Group"])["Sentiment"].mean().reset_index()
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=grouped_df, x="3_Hour_Group", y="Sentiment", hue="Ticker", marker="o")
    plt.title("3-Hourly Sentiment Trend", fontsize=16)
    plt.xlabel("3-Hour Time Group", fontsize=12)
    plt.ylabel("Average Sentiment", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(visible=True, linestyle='--', linewidth=0.5)
    plt.legend(title="Ticker")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.show()
    logging.info(f"3 小時情感趨勢圖已保存為 {output_path}")

# 主程式
if __name__ == "__main__":
    clear_directory("datasets")
    clear_directory("results")
    while True:
        ticker = input("請輸入股票代號（例如 TSLA 或 AAPL，輸入 'exit' 結束）：").strip()
        if ticker.lower() == "exit":
            break
        fetch_stock_data(ticker)
    news_df = parse_html_to_dataframe()
    if news_df is not None:
        news_df = process_time_column(news_df)
        clean_and_save_data(news_df)
        news_df = clean_headlines(news_df)
        news_df = analyze_sentiment(news_df)
        visualize_sentiment_by_3_hour(news_df)
        logging.info("流程完成！")