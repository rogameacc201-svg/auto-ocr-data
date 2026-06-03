import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import sys
from datetime import datetime

# 設定目標網址與請求標頭
URL = "https://www.pilio.idv.tw/bingo/list.asp"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_bingo_data():
    print("開始執行爬蟲程式...")
    try:
        # 1. 發送網頁請求
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.encoding = 'big5'
        
        if response.status_code != 200:
            print(f"網頁無法連線，狀態碼: {response.status_code}")
            return None

        # 2. 解析網頁內容
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()

        # 3. 使用正規表達式提取資料
        # 匹配格式: 期別: 1234567】 01, 02, ...
        pattern = re.compile(r'期別: (\d+)】\s+([\d, \s]+)')
        matches = pattern.findall(text_content)
        
        if not matches:
            print("未抓取到任何資料，網頁結構可能已變更。")
            return None

        print(f"成功抓取到 {len(matches)} 筆資料。")

        # 4. 整理資料格式
        data = []
        today = datetime.now().strftime('%Y-%m-%d')
        for m in matches:
            period = m[0]
            # 清除多餘空格並分割字串
            numbers = re.sub(r'\s+', '', m[1]).split(',')
            if len(numbers) >= 20:
                data.append([today, period] + numbers[:20])

        return pd.DataFrame(data, columns=['日期', '期別'] + [f'號碼{i+1}' for i in range(20)])

    except Exception as e:
        print(f"發生錯誤: {e}")
        return None

def save_data(new_df):
    file_path = "data.csv"
    
    if os.path.exists(file_path):
        # 讀取舊資料並合併
        old_df = pd.read_csv(file_path)
        # 合併後去除重複的期別
        final_df = pd.concat([new_df, old_df]).drop_duplicates(subset=['期別'])
        # 確保期別由新到舊排序
        final_df = final_df.sort_values(by='期別', ascending=False)
    else:
        final_df = new_df

    # 儲存為 UTF-8 格式
    final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print("資料已成功寫入 data.csv。")

if __name__ == "__main__":
    df = fetch_bingo_data()
    if df is not None:
        save_data(df)
    else:
        sys.exit(1) # 若抓取失敗則退出程式