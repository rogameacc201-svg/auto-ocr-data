import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

def run_scraper():
    print("--- 開始針對新結構抓取 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        content = response.content.decode('big5', errors='ignore')
        
        # 【修正關鍵】：直接匹配冒號後面的 9 位數字期別，以及後續的號碼行
        # \n\s* 處理換行，[\d, ]+ 匹配號碼行
        matches = re.findall(r':\s*(\d{9})\s*\n\s*([\d, \s]{50,})', content)
        
        data = []
        for period, nums_str in matches:
            # 提取所有兩位數號碼
            nums = re.findall(r'\d{2}', nums_str)
            if len(nums) >= 20:
                data.append([period] + nums[:20])
        
        if not data:
            print("依然無法匹配，結構可能還有變化。")
            return

        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        
        # 存檔邏輯 (保留舊資料)
        file_path = "data.csv"
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path, dtype={'期別': str})
            df['期別'] = df['期別'].astype(str)
            final_df = pd.concat([df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        else:
            final_df = df.sort_values(by='期別', ascending=False)
            
        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功抓取！共儲存 {len(final_df)} 筆資料。")
        print(final_df.head())
            
    except Exception as e:
        print(f"執行錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
