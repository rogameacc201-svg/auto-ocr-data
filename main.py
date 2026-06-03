import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'big5'
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    
    data = []
    # 精確鎖定：找 9 位數字(期別) 後面跟著 20 個數字(號碼)
    # 這樣會排除網頁上所有的標題、說明文字、廣告與舊連結
    matches = re.findall(r'(\d{9})\s+([\d\s]{50,})', text)
    
    for period, nums_str in matches:
        nums = re.findall(r'\b\d{2}\b', nums_str)
        # 嚴格過濾：必須剛好有 20 個號碼才視為有效
        if len(nums) == 20:
            data.append([period] + nums)
    
    if data:
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        # 將期別轉為日期欄位
        df['日期'] = df['期別'].apply(lambda x: f"20{x[1:3]}/{x[3:5]}/{x[5:7]}")
        cols = ['日期', '期別'] + [f'號碼{i+1}' for i in range(20)]
        df = df[cols].drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        df.to_csv("data.csv", index=False, encoding='utf-8-sig')
        print(f"成功儲存 {len(df)} 筆資料。")

if __name__ == "__main__":
    run_scraper()
