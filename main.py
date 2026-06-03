import requests
from bs4 import BeautifulSoup
import re

def run_scraper():
    print("--- 開始偵測 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        # 用 ignore 忽略無法解碼的字元，確保程式能跑完
        content = response.content.decode('big5', errors='ignore')
        
        # 【關鍵】：既然「期別」二字是亂碼，我們改用數字特徵來找
        # 尋找網頁中 1150605 這種格式的期別數字
        # 根據輸出，期別結構似乎是 [亂碼] + [數字]
        # 我們直接找連續的數字序列，或者更精確的模式
        
        print("--- 網頁完整文字內容 ---")
        print(content[:1000]) # 印出更多內容讓我們確認結構
        
        # 簡單測試：看看能不能找到任何數字
        all_numbers = re.findall(r'\d{7}', content)
        print(f"抓到的 7 位數字序列: {all_numbers[:10]}")
            
    except Exception as e:
        print(f"錯誤：{e}")

if __name__ == "__main__":
    run_scraper()
