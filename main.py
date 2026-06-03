import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import pytz
import os

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. 抓取網頁最新資料
    new_data = []
    table = soup.find('table', id='ltotable')
    if table:
        taipei_tz = pytz.timezone('Asia/Taipei')
        now_date = datetime.now(taipei_tz).strftime('%Y/%m/%d')
        
        for row in table.find_all('tr'):
            text = row.get_text()
            period_match = re.search(r'(\d{9})', text)
            if period_match:
                period = period_match.group(1)
                nums = re.findall(r'\b(\d{2})\b', text)
                if len(nums) >= 20:
                    new_data.append([now_date, period] + nums[:20])
    
    if not new_data:
        print("未抓取到資料")
        return

    # 將新資料轉為 DataFrame
    cols = ['日期', '期別'] + [f'號碼{i+1}' for i in range(20)]
    new_df = pd.DataFrame(new_data, columns=cols)
    
    # 2. 處理合併邏輯：保留舊資料，去重，覆蓋重複期別
    if os.path.exists("data.csv"):
        # 讀取舊資料
        old_df = pd.read_csv("data.csv", dtype={'期別': str})
        
        # 合併新舊資料
        # concat 後使用 drop_duplicates，keep='first' 會保留最上面那一筆 (即新抓到的那一筆)
        combined_df = pd.concat([new_df, old_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['期別'], keep='first')
    else:
        combined_df = new_df

    # 3. 排序並寫入
    # 確保期別是數值或字串，這裡用字串排序會較安全
    combined_df = combined_df.sort_values(by='期別', ascending=False)
    combined_df.to_csv("data.csv", index=False, encoding='utf-8-sig')
    
    print(f"處理完成，目前 data.csv 共有 {len(combined_df)} 筆資料。")

if __name__ == "__main__":
    run_scraper()
