import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime

URL = "https://www.pilio.idv.tw/bingo/list.asp"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

def run_scraper():
    print("--- 開始請求網頁 ---")
    response = requests.get(URL, headers=HEADERS, timeout=20)
    
    # 【自動備援機制】
    # 嘗試先用 utf-8 解碼，如果出現 UnicodeDecodeError，則強制轉為 big5
    try:
        content = response.content.decode('utf-8')
    except UnicodeDecodeError:
        print("偵測到非 UTF-8 編碼，切換為 BIG5...")
        content = response.content.decode('big5', errors='ignore')

    soup = BeautifulSoup(content, 'html.parser')
    text_content = soup.get_text()
    
    # 搜尋期別 (這裡的正規表達式必須配合該網頁實際的文字結構)
    pattern = re.compile(r'期別[:：]\s*(\d+)】\s*([\d,\s]+)')
    matches = pattern.findall(text_content)
    
    print(f"找到筆數: {len(matches)}")
    
    if not matches:
        # 如果還是抓不到，印出前 200 字方便診斷
        print("錯誤: 找不到資料，網頁文字片段如下：")
        print(text_content[:200])
        return

    # 整理資料
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
    print("檔案已成功更新。")

if __name__ == "__main__":
    run_scraper()
