from bs4 import BeautifulSoup
import os
import pandas as pd

def parse_html_to_dataframe():
    """
    解析 datasets 資料夾中的 HTML 檔案，提取新聞標題和時間資訊，返回 DataFrame
    """
    # 確保 datasets 資料夾存在
    if not os.path.exists("datasets"):
        print("datasets 資料夾不存在，請先執行爬取步驟。")
        return None

    parsed_news = []
    
    # 遍歷 datasets 資料夾中的 HTML 檔案
    for file_name in os.listdir("datasets"):
        file_path = os.path.join("datasets", file_name)
        ticker = file_name.split("_")[0].upper()  # 從檔案名提取股票代號

        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            news_table = soup.find(id="news-table")
            
            if not news_table:
                print(f"未在 {file_name} 中找到 'news-table'，跳過該檔案...")
                continue

            # 提取每條新聞的標題和時間
            for row in news_table.findAll("tr"):
                headline = row.a.get_text(strip=True)
                time_text = row.td.get_text(strip=True)
                parsed_news.append([ticker, time_text, headline])

    # 將提取的數據轉換為 DataFrame
    news_df = pd.DataFrame(parsed_news, columns=["Ticker", "Time", "Headline"])
    return news_df

# 主程式
if __name__ == "__main__":
    news_df = parse_html_to_dataframe()
    if news_df is not None:
        print(news_df.head())  # 顯示前幾筆資料
        
        # 確保 results 資料夾存在
        os.makedirs("results", exist_ok=True)

        # 保存 DataFrame 為 CSV 檔案
        news_df.to_csv("results/news_data.csv", index=False)
        print("新聞資料已保存到 results/news_data.csv")