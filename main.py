import requests
from bs4 import BeautifulSoup
import re

def run_scraper():
    print("--- 開始偵測 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        
        # 【核心修正】：不要只靠 encoding，直接用 raw content 用 big5 解碼
        # 這是處理繁體中文舊網站最穩定的做法
        content = response.content.decode('big5', errors='ignore')
        
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        
        # 列印片段測試
        print(f"網頁內容預覽: {text[:100]}...")
        
        if "期別" in text:
            print("結果：成功抓到網頁文字！")
            # 這裡之後可以加入你的正規表達式邏輯
        else:
            print("結果：警告，依然找不到 '期別'，網站結構可能已大幅變更。")
            
    except Exception as e:
        print(f"錯誤：{e}")

if __name__ == "__main__":
    run_scraper()
