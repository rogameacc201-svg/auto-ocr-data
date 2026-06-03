import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import pytz

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = []
    table = soup.find('table', id='ltotable')
    if table:
        # 設定時區為台北時間
        taipei_tz = pytz.timezone('Asia/Taipei')
        now_date = datetime.now(taipei_tz).strftime('%Y/%m/%d')
        
        for row in table.find_all('tr'):
            text = row.get_text()
            period_match = re.search(r'(\d{9})', text)
            if period_match:
                period = period_match.group(1)
                nums = re.findall(r'\b(\d{2})\b', text)
                if len(nums) >= 20:
                    # 直接寫入當前系統日期
                    data.append([now_date, period] + nums[:20])
    
    if data:
        df = pd.DataFrame(data, columns=['日期', '期別'] + [f'號碼{i+1}' for i in range(20)])
        # 依照期別由新到舊排序
        df = df.sort_values(by='期別', ascending=False)
        df.to_csv("data.csv", index=False, encoding='utf-8-sig')
        print(f"成功儲存 {len(df)} 筆資料，日期標記為 {now_date}")

if __name__ == "__main__":
    run_scraper()
