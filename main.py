import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime

# 目標網站設定
URL = "https://www.pilio.idv.tw/bingo/list.asp"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def run_scraper():
    print("--- 開始請求網頁 ---")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        # 自動識別編碼，若識別為 ISO-8859-1 (常是 Big5 網站誤判)，強制設為 big5
        if response.encoding == 'ISO-8859-1':
            response.encoding = 'big5'
        
        print(f"狀態碼: {response.status_code}, 編碼: {response.encoding}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        
        # 搜尋期別 (支援半形/全形冒號)
        pattern = re.compile(r'期別[:：]\s*(\d+)】\s*([\d,\s]+)')
        matches = pattern.findall(text_content)
        
        if not matches:
            print("未抓取到資料，可能是網頁結構變更。")
            return

        today = datetime.now().strftime('%Y-%m-%d')
        new_data = [[today, m[0]] + re.sub(r'\s+', '', m[1]).split(',')[:20] for m in matches]
        new_df = pd.DataFrame(new_data, columns=['日期', '期別'] + [f'號碼{i+1}' for i in range(20)])
        
        file_path = "data.csv"
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path)
            final_df = pd.concat([new_df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        else:
            final_df = new_df

        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print("成功更新 data.csv")
        
    except Exception as e:
        print(f"執行時發生錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
