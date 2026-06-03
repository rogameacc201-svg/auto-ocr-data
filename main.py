import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

def run_scraper():
    # 使用原本有效的方法
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'big5'
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    
    data = []
    # 這是你原本有效的分塊邏輯
    blocks = re.split(r':\s*', text)
    for block in blocks:
        period_match = re.search(r'\d{9}', block)
        if period_match:
            period = period_match.group()
            nums = re.findall(r'\b\d{2}\b', block)
            if len(nums) >= 20:
                data.append([period] + nums[:20])
    
    if data:
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        # 加上日期欄位方便 html 讀取
        df['日期'] = df['期別'].apply(lambda x: f"20{x[1:3]}/{x[3:5]}/{x[5:7]}")
        df.to_csv("data.csv", index=False, encoding='utf-8-sig')
        print(f"成功儲存 {len(df)} 筆資料。")

if __name__ == "__main__":
    run_scraper()
