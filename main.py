import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    response.encoding = 'big5'
    
    # 儲存一份 raw.txt，讓你檢查 Python 到底抓到了什麼
    with open("raw.txt", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    
    # 修改後的 Regex：允許更多空格和符號，確保更寬鬆的匹配
    matches = re.findall(r'(\d{9}).*?([\d\s]{50,})', text, re.DOTALL)
    
    data = []
    for period, nums_str in matches:
        nums = re.findall(r'\b\d{2}\b', nums_str)
        if len(nums) >= 20:
            data.append([period] + nums[:20])
    
    if data:
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        df.to_csv("data.csv", index=False, encoding='utf-8-sig')
        print(f"成功抓到 {len(df)} 筆資料。")
    else:
        print("未抓到任何資料，請檢查 raw.txt 確認網頁內容。")

if __name__ == "__main__":
    run_scraper()
