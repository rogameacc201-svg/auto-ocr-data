import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime

URL = "https://www.pilio.idv.tw/bingo/list.asp"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

def run_scraper():
    print("--- 1. 開始發送請求 ---")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        print(f"狀態碼: {response.status_code}")
        response.encoding = 'big5'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        
        print("--- 2. 開始搜尋資料 ---")
        pattern = re.compile(r'期別: (\d+)】\s+([\d, \s]+)')
        matches = pattern.findall(text_content)
        
        print(f"找到的資料筆數: {len(matches)}")
        
        if not matches:
            print("錯誤: 正規表達式未匹配到任何內容。")
            return

        # 整理資料
        data = []
        today = datetime.now().strftime('%Y-%m-%d')
        for m in matches:
            period = m[0]
            numbers = re.sub(r'\s+', '', m[1]).split(',')
            if len(numbers) >= 20:
                data.append([today, period] + numbers[:20])

        new_df = pd.DataFrame(data, columns=['日期', '期別'] + [f'號碼{i+1}' for i in range(20)])
        
        # 寫入檔案
        file_path = "data.csv"
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path)
            final_df = pd.concat([new_df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
            print("已合併舊資料。")
        else:
            final_df = new_df
            print("建立新檔案。")

        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print("成功寫入 data.csv")

    except Exception as e:
        print(f"發生嚴重錯誤: {str(e)}")
        raise e # 讓我們在 Action 中明確看到錯誤

if __name__ == "__main__":
    run_scraper()
