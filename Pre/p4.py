import requests
import os
import shutil
from bs4 import BeautifulSoup
import pandas as pd
import logging

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def clear_directory(directory):
    """
    清空指定資料夾中的所有檔案和子資料夾
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)  # 刪除資料夾及其內容
        logging.info(f"已清空資料夾: {directory}")
    os.makedirs(directory, exist_ok=True)  # 重新創建空資料夾

def fetch_stock_data(ticker):
    """
    爬取指定股票的 Finviz 新聞頁面 HTML 並保存到 datasets 資料夾
    """
    url = f"https://finviz.com/quote.ashx?t={ticker.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    # 發送 GET 請求
    response = requests.get(url, headers=headers)
    os.makedirs("datasets", exist_ok=True)
    
    if response.status_code == 200:
        file_name = f"{ticker.lower()}_finviz.html"
        file_path = os.path.join("datasets", file_name)
        
        # 保存 HTML 到檔案
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
        logging.info(f"{ticker.upper()} 的 HTML 已成功保存到 {file_path}")
    else:
        logging.error(f"無法獲取 {ticker.upper()} 資料，HTTP 狀態碼: {response.status_code}")

def parse_html_to_dataframe(directory="datasets"):
    """
    解析 datasets 資料夾中的 HTML 檔案，提取新聞標題和時間資訊，返回 DataFrame
    """
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

                for row in news_table.findAll("tr"):
                    headline = row.a.get_text(strip=True)
                    time_text = row.td.get_text(strip=True)
                    parsed_news.append([ticker, time_text, headline])
        
        except Exception as e:
            logging.error(f"解析 {file_name} 時出現錯誤: {e}")
    
    news_df = pd.DataFrame(parsed_news, columns=["Ticker", "Time", "Headline"])
    return news_df

def clean_and_save_data(df, output_path="results/news_data.csv"):
    """
    清理數據並保存為 CSV 檔案
    """
    df["Time"] = df["Time"].str.replace(r"\s+", " ", regex=True).str.strip()
    df["Headline"] = df["Headline"].str.strip()
    df = df.drop_duplicates()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logging.info(f"數據已保存到 {output_path}")

if __name__ == "__main__":
    # 清空資料夾
    clear_directory("datasets")
    clear_directory("results")

    # 爬取數據
    while True:
        ticker = input("請輸入股票代號（例如 TSLA 或 AAPL，輸入 'exit' 結束）：").strip()
        if ticker.lower() == "exit":
            break
        fetch_stock_data(ticker)
    
    # 解析數據並保存
    logging.info("開始解析 HTML 並生成數據...")
    news_df = parse_html_to_dataframe()
    if news_df is not None:
        clean_and_save_data(news_df)
        logging.info("解析和保存完成！")