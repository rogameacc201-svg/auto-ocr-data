import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def run_scraper():
    url = "https://www.pilio.idv.tw/bingo/list.asp"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://www.pilio.idv.tw/bingo/list.asp',
        'Accept-Language': 'zh-TW,zh;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8' # 現代網頁通常已轉為 utf-8
        
        # 保存 raw.txt 以供除錯
        with open("raw.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 根據 raw.txt，期別和號碼位於 table#ltotable 的 tr > td 中
        data = []
        table = soup.find('table', id='ltotable')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                text = row.get_text()
                # 匹配期別 (如: 115031168)
                period_match = re.search(r'(\d{9})', text)
                if period_match:
                    period = period_match.group(1)
                    # 匹配所有兩位數字的號碼
                    nums = re.findall(r'\b(\d{2})\b', text)
                    if len(nums) >= 20:
                        data.append([period] + nums[:20])
        
        if data:
            df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
            df.to_csv("data.csv", index=False, encoding='utf-8-sig')
            print(f"成功抓取 {len(df)} 筆資料。")
        else:
            print("未能從表格中解析出期別與號碼，請確認網頁結構是否更動。")
            
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
