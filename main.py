import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import shutil
from datetime import datetime
import pytz

def run_scraper():
    # 1. 設定網址與標頭
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 2. 抓取網頁資料
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"網頁讀取失敗: {e}")
        return
    
    new_data = []
    table = soup.find('table', id='ltotable')
    
    if table:
        for row in table.find_all('tr'):
            text = row.get_text()
            period_match = re.search(r'(\d{9})', text)
            if period_match:
                period = period_match.group(1)
                nums = re.findall(r'\b(\d{2})\b', text)
                if len(nums) >= 20:
                    new_data.append([period] + nums[:20])

    if not new_data:
        print("未抓取到資料")
        return

    # 3. 準備新資料的 DataFrame
    cols = ['期別'] + [f'號碼{i+1}' for i in range(20)]
    new_df = pd.DataFrame(new_data, columns=cols)
    
    # 計算今天日期 (Asia/Taipei)
    taipei_tz = pytz.timezone('Asia/Taipei')
    today_str = datetime.now(taipei_tz).strftime('%Y/%m/%d')

    # 4. 處理合併與日期保護
    if os.path.exists("data.csv"):
        # 建立備份，萬一出錯隨時可以救回
        shutil.copy("data.csv", "data_backup.csv")
        
        old_df = pd.read_csv("data.csv", dtype={'期別': str})
        
        # 將新舊資料合併
        combined_df = pd.concat([new_df, old_df], ignore_index=True)
        # 根據期別去重，保留最新抓到的那一筆
        combined_df = combined_df.drop_duplicates(subset=['期別'], keep='first')
        
        # 【核心修正】：只針對「沒有日期」的資料填上今天日期
        # 這樣舊資料原本的日期就不會被覆蓋
        combined_df['日期'] = combined_df['日期'].fillna(today_str)
    else:
        # 如果是第一次建立，全部標記為今天
        new_df['日期'] = today_str
        combined_df = new_df

    # 5. 確保欄位順序並排序
    final_cols = ['日期', '期別'] + [f'號碼{i+1}' for i in range(20)]
    combined_df = combined_df[final_cols]
    combined_df = combined_df.sort_values(by='期別', ascending=False)
    
    # 6. 儲存 CSV
    combined_df.to_csv("data.csv", index=False, encoding='utf-8-sig')
    print(f"處理完成！目前資料庫共有 {len(combined_df)} 筆。")

if __name__ == "__main__":
    run_scraper()
