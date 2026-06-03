import requests
import re
import pandas as pd
import os

def run_scraper():
    print("--- 執行暴力模式匹配 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        # 用 big5 解碼並忽略錯誤，直接獲取純文字
        text = response.content.decode('big5', errors='ignore')
        
        # 尋找所有 2 位數的組合，賓果號碼通常是 01-80
        # 我們抓取網頁中所有連續出現的 2 位數字 (這裡排除期別的 7 位數)
        nums = re.findall(r'\b(\d{2})\b', text)
        
        # 賓果每期 20 個號碼，加上期別 (假設期別緊鄰在號碼前)
        # 我們嘗試從文字中找出長度為 21 的數字序列
        data = []
        # 我們使用滑動視窗找尋可能的序列
        for i in range(len(nums) - 20):
            # 檢查是否有連續 20 個號碼 (數字範圍 01-80)
            chunk = nums[i:i+20]
            if all(1 <= int(n) <= 80 for n in chunk):
                # 假設前一個是期別 (這裡期別長度不固定，暫時先略過期別，只抓號碼)
                data.append(chunk)
                
        if not data:
            print("警告: 依然抓不到數字組合，網站可能封鎖了爬蟲。")
            return

        # 這裡會存入號碼，期別部分我們後續再優化
        df = pd.DataFrame(data, columns=[f'號碼{i+1}' for i in range(20)])
        
        file_path = "data.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功抓取到 {len(df)} 組號碼序列。")
            
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
