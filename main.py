import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

def run_scraper():
    print("--- 開始爬取與寫入 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        content = response.content.decode('big5', errors='ignore')
        
        # 尋找所有 7 位數字序列
        all_numbers = re.findall(r'\d{7}', content)
        # 去除重複，並排序 (最新的期別通常數字較大)
        unique_periods = sorted(list(set(all_numbers)), reverse=True)
        
        print(f"整理後的期別清單: {unique_periods[:5]}")
        
        # 建立 DataFrame 並存檔
        data = {'期別': unique_periods}
        df = pd.DataFrame(data)
        
        file_path = "data.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功更新 {file_path}，共儲存 {len(unique_periods)} 筆期別。")
            
    except Exception as e:
        print(f"錯誤：{e}")

if __name__ == "__main__":
    run_scraper()
