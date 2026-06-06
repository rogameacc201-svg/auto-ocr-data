import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import shutil
from datetime import datetime
import pytz

# 強制設定時區為台北，確保日期計算不誤差
os.environ['TZ'] = 'Asia/Taipei'

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 1. 抓取網頁資料
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

    # 2. 準備新資料的 DataFrame
    cols = ['期別'] + [f'號碼{i+1}' for i in range(20)]
    new_df = pd.DataFrame(new_data, columns=cols)
    
    # 計算今天日期 (台北時間)
    taipei_tz = pytz.timezone('Asia/Taipei')
    today_str = datetime.now(taipei_tz).strftime('%Y/%m/%d')

    # 3. 處理合併與日期保護
    if os.path.exists("data.csv"):
        # 備份機制：確保出錯時有檔案可救
        shutil.copy("data.csv", "data_backup.csv")
        
        old_df = pd.read_csv("data.csv", dtype={'期別': str})
        
        # 【效能優化】：檢查是否有新期別，若所有新抓到的期別都已在舊檔中，直接停止，不進行寫入
        if new_df['期別'].isin(old_df['期別']).all():
            print("目前無新期別，無需更新。")
            return
        
        # 合併新舊資料 (舊資料優先)
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
        
        # 去重：只保留第一次出現的期別 (舊資料優先)
        combined_df = combined_df.drop_duplicates(subset=['期別'], keep='first')
        
        # 填補日期：只針對沒有日期的資料填入今天日期
        combined_df['日期'] = combined_df['日期'].fillna(today_str)
    else:
        # 第一次建立檔案時
        new_df['日期'] = today_str
        combined_df = new_df

    # 4. 確保欄位順序並排序
    final_cols = ['日期', '期別'] + [f'號碼{i+1}' for i in range(20)]
    combined_df = combined_df[final_cols]
    combined_df = combined_df.sort_values(by='期別', ascending=False)
    
    # 5. 寫入檔案
    combined_df.to_csv("data.csv", index=False, encoding='utf-8-sig')
    print(f"處理完成！目前資料庫共有 {len(combined_df)} 筆。")

if __name__ == "__main__":
    run_scraper()
