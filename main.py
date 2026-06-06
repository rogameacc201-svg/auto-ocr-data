import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import shutil
from datetime import datetime
import pytz

# 強制設定時區為台北
os.environ['TZ'] = 'Asia/Taipei'

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
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
                # 關鍵修改：抓取數字後使用 int() 轉換，自動移除前導零
                nums_raw = re.findall(r'\b(\d{2})\b', text)
                if len(nums_raw) >= 20:
                    nums_clean = [str(int(n)) for n in nums_raw[:20]]
                    new_data.append([period] + nums_clean)

    if not new_data:
        print("未抓取到資料")
        return

    cols = ['期別'] + [f'號碼{i+1}' for i in range(20)]
    new_df = pd.DataFrame(new_data, columns=cols)
    
    taipei_tz = pytz.timezone('Asia/Taipei')
    today_str = datetime.now(taipei_tz).strftime('%Y/%m/%d')

    if os.path.exists("data.csv"):
        shutil.copy("data.csv", "data_backup.csv")
        old_df = pd.read_csv("data.csv", dtype={'期別': str})
        
        # 效能優化：無新期別不動作
        if new_df['期別'].isin(old_df['期別']).all():
            print("目前無新期別，無需更新。")
            return
        
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['期別'], keep='first')
        combined_df['日期'] = combined_df['日期'].fillna(today_str)
    else:
        new_df['日期'] = today_str
        combined_df = new_df

    final_cols = ['日期', '期別'] + [f'號碼{i+1}' for i in range(20)]
    combined_df = combined_df[final_cols]
    combined_df = combined_df.sort_values(by='期別', ascending=False)
    
    combined_df.to_csv("data.csv", index=False, encoding='utf-8-sig')
    print(f"處理完成！已去除前導零，共有 {len(combined_df)} 筆資料。")

if __name__ == "__main__":
    run_scraper()
