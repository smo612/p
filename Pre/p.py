import requests
import os

def fetch_stock_data(ticker):
    """
    爬取指定股票的 Finviz 新聞頁面 HTML 並保存到 datasets 資料夾
    """
    # 動態生成 URL
    url = f"https://finviz.com/quote.ashx?t={ticker.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    # 發送 GET 請求
    response = requests.get(url, headers=headers)
    
    # 確保 datasets 資料夾存在
    os.makedirs("datasets", exist_ok=True)
    
    if response.status_code == 200:
        # 自動命名檔案
        file_name = f"{ticker.lower()}_finviz.html"
        file_path = os.path.join("datasets", file_name)
        
        # 保存 HTML 到檔案
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"{ticker.upper()} 的 HTML 已成功保存到 {file_path}")
    else:
        print(f"無法獲取 {ticker.upper()} 資料，HTTP 狀態碼: {response.status_code}")

# 主程式
if __name__ == "__main__":
    while True:
        # 提示使用者輸入股票代號
        ticker = input("請輸入股票代號（例如 TSLA 或 AAPL，輸入 'exit' 結束）：").strip()
        
        if ticker.lower() == "exit":
            print("結束爬取作業。")
            break
        
        # 呼叫函數爬取資料
        fetch_stock_data(ticker)