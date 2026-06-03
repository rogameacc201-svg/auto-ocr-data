import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime

# 目標網站設定
URL = "https://www.pilio.idv.tw/bingo/list.asp"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

def run_scraper():
    print("--- 1. 開始發送請求 ---")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        
        # 【關鍵修正】強制編碼設定，若網站編碼自動判斷異常，使用 apparent_encoding
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding
        
        print(f"狀態碼: {response.status_code}, 目前編碼: {response.encoding}")
        
        # 如果你確定該網站是 UTF-8，可取消下方註解強制設定
        # response.encoding = 'utf-8' 

        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        
        print("--- 2. 開始搜尋資料 ---")
        # 正規表達式：請確認網頁原始碼中的標籤格式是否符合此規則
        pattern = re.compile(r'期別: (\d+)】\s+([\d, \s]+)')
        matches = pattern.findall(text_content)
        
        print(f"找到的資料筆數: {len(matches)}")
        
        if not matches:
            print("警告: 正規表達式未匹配到任何內容，請檢查網頁結構。")
            return

        # 整理資料
        data = []
        today = datetime.now().strftime('%Y-%m-%d')
        for m in matches:
            period = m[0]
            # 清除空格並用逗號分割數字
            numbers = re.sub(r'\s+', '', m[1]).split(',')
            # 賓果通常是 20 個號碼，確保資料長度正確
            if len(numbers) >= 20:
                data.append([today, period] + numbers[:20])

        new_df = pd.DataFrame(data, columns=['日期', '期別'] + [f'號碼{i+1}' for i in range(20)])
        
        # 強制路徑為根目錄
        file_path = "data.csv"
        
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path)
            # 合併新舊資料，移除重複期別，並按期別降冪排列
            final_df = pd.concat([new_df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
            print("已合併舊資料。")
        else:
            final_df = new_df
            print("建立新檔案。")

        # 寫入 CSV
        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功更新檔案至 {file_path}")

    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        # 為了讓 GitHub Actions 識別錯誤，這裡拋出異常
        raise e

if __name__ == "__main__":
    run_scraper()
