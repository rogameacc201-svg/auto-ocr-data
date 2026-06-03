import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import pytz
import os
import time
import random

def run_scraper():
    # 隨機延遲 1-3 秒，模擬真人行為，避免被網站封鎖
    time.sleep(random.uniform(1, 3))
    
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = []
        table = soup.find('table', id='ltotable')
        if not table:
            print("找不到表格資料")
            return

        taipei_tz = pytz.timezone('Asia/Taipei')
        now_str = datetime.now(taipei_tz).strftime('%Y/%m/%d %H:%M')
        date_key = datetime.now(taipei_tz).strftime('%Y/%m/%d')
        
        for row in table.find_all('tr'):
            text = row.get_text()
            period_match = re.search(r'(\d{9})', text)
            if period_match:
                period = period_match.group(1)
                nums = re.findall(r'\b(\d{2})\b', text)
                if len(nums) >= 20:
                    data.append([date_key, now_str, period] + nums[:20])
        
        if data:
            df = pd.DataFrame(data, columns=['日期', '時間', '期別'] + [f'號碼{i+1}' for i in range(20)])
            
            # 若已存在檔案，讀取並過濾掉重複的期別，避免重複寫入
            if os.path.exists('data.csv'):
                old_df = pd.read_csv('data.csv', encoding='utf-8-sig')
                df = pd.concat([df, old_df]).drop_duplicates(subset=['期別'])
            
            df = df.sort_values(by='期別', ascending=False)
            df.to_csv("data.csv", index=False, encoding='utf-8-sig')
            print(f"成功更新，目前共 {len(df)} 筆資料")
            
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
