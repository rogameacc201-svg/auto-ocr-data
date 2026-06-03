import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. 讀取現有的 CSV (如果存在)
    if os.path.exists("data.csv"):
        old_df = pd.read_csv("data.csv", dtype={'期別': str})
    else:
        old_df = pd.DataFrame(columns=['日期', '期別'] + [f'號碼{i+1}' for i in range(20)])

    new_rows = []
    table = soup.find('table', id='ltotable')
    
    if table:
        for row in table.find_all('tr'):
            text = row.get_text()
            period_match = re.search(r'(\d{9})', text)
            
            if period_match:
                period = period_match.group(1)
                nums = re.findall(r'\b(\d{2})\b', text)
                
                if len(nums) >= 20:
                    # 關鍵修正：檢查該期別是否已經存在
                    if period in old_df['期別'].values:
                        # 如果已存在，保留該期別原本的日期 (不做更改)
                        continue 
                    else:
                        # 如果是新期別，才標記為當天日期
                        from datetime import datetime
                        import pytz
                        taipei_tz = pytz.timezone('Asia/Taipei')
                        new_date = datetime.now(taipei_tz).strftime('%Y/%m/%d')
                        new_rows.append([new_date, period] + nums[:20])

    # 2. 合併新舊資料
    if new_rows:
        new_df = pd.DataFrame(new_rows, columns=['日期', '期別'] + [f'號碼{i+1}' for i in range(20)])
        combined_df = pd.concat([new_df, old_df], ignore_index=True)
    else:
        combined_df = old_df

    # 3. 排序並寫入
    combined_df = combined_df.sort_values(by='期別', ascending=False)
    combined_df.to_csv("data.csv", index=False, encoding='utf-8-sig')
    print(f"處理完成，目前資料庫共有 {len(combined_df)} 筆。")

if __name__ == "__main__":
    run_scraper()
