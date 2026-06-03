import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime

URL = "https://www.pilio.idv.tw/bingo/list.asp"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def run_scraper():
    print("1. 發送請求...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        if response.encoding == 'ISO-8859-1':
            response.encoding = 'big5'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        # 尋找期別
        matches = re.findall(r'期別[:：]\s*(\d+)', text)
        print(f"2. 在網頁中找到的期別 ID 列表: {matches[:10]}")
        
        if not matches:
            print("!!! 錯誤: 在網頁中找不到任何期別，爬蟲結構可能失效。")
            return

        # 簡單檢查最後一期
        latest_period = matches[0]
        print(f"3. 偵測到最新一期為: {latest_period}")
        
        file_path = "data.csv"
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path)
            # 檢查最後一期是否已經存在
            if str(latest_period) in old_df['期別'].astype(str).values:
                print(f"4. 最新一期 {latest_period} 已存在，無需更新。")
            else:
                print("5. 發現新資料，準備寫入！")
                # (這裡省略寫入細節，確保邏輯正確)
        else:
            print("5. 沒有舊檔案，建立新檔案。")

    except Exception as e:
        print(f"!!! 執行錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
