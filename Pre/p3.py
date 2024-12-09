from bs4 import BeautifulSoup
import os
import pandas as pd
import logging

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_html_to_dataframe(directory="datasets"):
    """
    解析指定資料夾中的 HTML 檔案，提取新聞標題和時間資訊，返回 DataFrame
    """
    # 確保資料夾存在
    if not os.path.exists(directory):
        logging.error(f"{directory} 資料夾不存在，請確認檔案路徑。")
        return None

    parsed_news = []

    # 遍歷資料夾中的 HTML 檔案
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        ticker = file_name.split("_")[0].upper()  # 從檔案名提取股票代號

        try:
            # 解析 HTML
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
                news_table = soup.find(id="news-table")
                
                if not news_table:
                    logging.warning(f"未在 {file_name} 中找到 'news-table'，跳過該檔案。")
                    continue

                # 提取每條新聞的標題和時間
                for row in news_table.findAll("tr"):
                    headline = row.a.get_text(strip=True)
                    time_text = row.td.get_text(strip=True)
                    parsed_news.append([ticker, time_text, headline])
        
        except Exception as e:
            logging.error(f"解析 {file_name} 時出現錯誤: {e}")
    
    # 創建 DataFrame
    news_df = pd.DataFrame(parsed_news, columns=["Ticker", "Time", "Headline"])
    return news_df


def clean_and_save_data(df, output_path="results/news_data.csv"):
    """
    清理數據並保存為 CSV 檔案
    """
    # 去除多餘空白和換行
    df["Time"] = df["Time"].str.replace(r"\s+", " ", regex=True).str.strip()
    df["Headline"] = df["Headline"].str.strip()

    # 去重
    df = df.drop_duplicates()

    # 確保目標資料夾存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 保存為 CSV
    df.to_csv(output_path, index=False)
    logging.info(f"數據已保存到 {output_path}")


def display_head_by_ticker(df, n=5):
    """
    分別顯示每個股票代號的前 n 條新聞
    """
    grouped = df.groupby("Ticker")
    for ticker, group in grouped:
        print(f"\n{ticker} 的前 {n} 項新聞：")
        print(group.head(n), "\n")


# 主程式
if __name__ == "__main__":
    # 解析 HTML 並生成 DataFrame
    news_df = parse_html_to_dataframe()

    if news_df is not None:
        logging.info("成功解析 HTML 檔案，數據預覽：")
        print(news_df.head())  # 預覽數據

        # 清理並保存數據
        clean_and_save_data(news_df)

        # 分別顯示每個股票代號的前 5 條新聞
        display_head_by_ticker(news_df, n=5)