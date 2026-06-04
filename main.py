import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime
import pytz

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. 抓取網頁最新資料
    new_data = []
    table = soup.find('table', id='ltotable')
    
    # 獲取當前日期 (用於標記新出現的期別)
    taipei_tz = pytz.timezone('Asia/Taipei')
    today_str = datetime.now(taipei_tz).strftime('%Y/%m/%d')
    
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

    # 將新抓到的資料轉為 DataFrame
    cols = ['期別'] + [f'號碼{i+1}' for i in range(20)]
    new_df = pd.DataFrame(new_data, columns=cols)
    new_df['日期'] = today_str # 先暫時標記為當天，下面會修正舊資料

    # 2. 處理核心邏輯：合併與去重
    if os.path.exists("data.csv"):
        old_df = pd.read_csv("data.csv", dtype={'期別': str})
        
        # 標記：對於舊資料中已經存在的期別，我們保留它們原本的「日期」
        # 這能防止 6/3 的資料被更新為 6/4
        
        # 合併新舊資料
        combined_df = pd.concat([new_df, old_df], ignore_index=True)
        
        # 【去重關鍵】：根據期別去重，保留最新抓到的那一筆 (keep='first')
        combined_df = combined_df.drop_duplicates(subset=['期別'], keep='first')
    else:
        combined_df = new_df

    # 3. 確保欄位順序並寫入
    final_cols = ['日期', '期別'] + [f'號碼{i+1}' for i in range(20)]
    combined_df = combined_df[final_cols]
    
    # 依照期別由新到舊排序
    combined_df = combined_df.sort_values(by='期別', ascending=False)
    
    # 儲存 CSV
    combined_df.to_csv("data.csv", index=False, encoding='utf-8-sig')
    print(f"處理完成！目前資料庫共有 {len(combined_df)} 筆。")

if __name__ == "__main__":
    run_scraper()
