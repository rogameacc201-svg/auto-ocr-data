import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = []
    table = soup.find('table', id='ltotable')
    if table:
        for row in table.find_all('tr'):
            text = row.get_text()
            period_match = re.search(r'(\d{9})', text)
            if period_match:
                period = period_match.group(1)
                nums = re.findall(r'\b(\d{2})\b', text)
                if len(nums) >= 20:
                    data.append([period] + nums[:20])
    
    if data:
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        # 強制加入日期欄位並排在最前
        df['日期'] = df['期別'].apply(lambda x: f"20{x[1:3]}/{x[3:5]}/{x[5:7]}")
        cols = ['日期', '期別'] + [f'號碼{i+1}' for i in range(20)]
        df = df[cols].sort_values(by='期別', ascending=False)
        
        df.to_csv("data.csv", index=False, encoding='utf-8-sig')
        print(f"成功儲存 {len(df)} 筆資料。")

if __name__ == "__main__":
    run_scraper()
