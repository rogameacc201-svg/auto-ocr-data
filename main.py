import requests
import pandas as pd
import os
from bs4 import BeautifulSoup

def run_scraper():
    print("--- 開始偵測 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    try:
        r = requests.get(URL, timeout=10)
        r.encoding = 'big5'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 抓取網頁上所有文字來看看
        content = soup.get_text()
        print(f"網頁內容預覽: {content[:100]}...") # 只印前100字
        
        if "期別" in content:
            print("結果：成功抓到網頁文字！")
        else:
            print("結果：警告，找不到關鍵字 '期別'，網站可能改版了。")
            
    except Exception as e:
        print(f"錯誤：{e}")

if __name__ == "__main__":
    run_scraper()
