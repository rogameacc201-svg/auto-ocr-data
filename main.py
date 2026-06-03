import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime

URL = "https://www.pilio.idv.tw/bingo/list.asp"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

def run_scraper():
    print("--- 開始執行爬蟲 ---")
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text()

    # 搜尋期別
    pattern = re.compile(r'期別: (\d+)】\s+([\d, \s]+)')
    matches = pattern.findall(text_content)
    
    print(f"找到 matches 數量: {len(matches)}")
    
    if not matches:
        print("警告: 正規表達式未抓取到任何資料！")
        return

    # 整理資料
    today = datetime.now().strftime('%Y-%m-%d')
    new_data = []
    for m in matches:
        period = m[0]
        numbers = re.sub(r'\s+', '', m[1]).split(',')
        if len(numbers) >= 20:
            new_data.append([today, period] + numbers[:20])

    new_df = pd.DataFrame(new_data, columns=['日期', '期別'] + [f'號碼{i+1}' for i in range(20)])
    
    # 強制檢查 data.csv
    file_path = "data.csv"
    if os.path.exists(file_path):
        print(f"找到舊檔案: {file_path}")
        old_df = pd.read_csv(file_path)
        final_df = pd.concat([new_df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
    else:
        print("沒有找到舊檔案，建立新檔案")
        final_df = new_df

    final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print("檔案已儲存完畢。")

if __name__ == "__main__":
    run_scraper()
