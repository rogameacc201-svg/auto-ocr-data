import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime

URL = "https://www.pilio.idv.tw/bingo/list.asp"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def run_scraper():
    print("--- 開始請求網頁 ---")
    response = requests.get(URL, headers=HEADERS, timeout=20)
    if response.encoding == 'ISO-8859-1':
        response.encoding = 'big5'
        
    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = soup.get_text()

    # 【除錯重點】：如果不確定網頁結構，我們先把抓到的關鍵文字印出來
    # 如果這裡沒抓到，我們之後調整正規表達式
    print("--- 偵測到的網頁內容片段 ---")
    print(text_content[:500]) 
    
    # 修改正規表達式，讓它更寬鬆一點 (尋找 '期別' 之後的數字)
    pattern = re.compile(r'期別[:：]?\s*(\d+)')
    matches = pattern.findall(text_content)
    
    print(f"找到的期別 ID: {matches[:5]}")
    
    if not matches:
        print("警告: 完全找不到期別資訊，請檢查網頁是否改版。")
        return

    # 若這裡有印出期別，代表我們可以成功抓到資料，
    # 接下來請你把 Run script 的完整輸出內容貼給我。
    print("成功抓到期別，準備進行後續處理...")

if __name__ == "__main__":
    run_scraper()
