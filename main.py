import requests
import re
import pandas as pd
import os

def run_scraper():
    print("--- 開始全面抓取期別 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        # 用 big5 解碼並忽略亂碼
        content = response.content.decode('big5', errors='ignore')
        
        # 尋找網頁中所有連續 7 位的數字 (這是期別特徵)
        # 這裡不使用 set()，確保可以看到所有出現過的期別
        all_periods = re.findall(r'\d{7}', content)
        
        print(f"總共在網頁中找到的 7 位數字組合數量: {len(all_periods)}")
        print(f"前 50 個數字片段: {all_periods[:50]}")
        
        if len(all_periods) > 0:
            # 將資料存入 DataFrame
            df = pd.DataFrame(all_periods, columns=['期別'])
            
            # 如果你有歷史資料檔案，我們進行合併與去重，確保不遺失
            file_path = "data.csv"
            if os.path.exists(file_path):
                old_df = pd.read_csv(file_path)
                final_df = pd.concat([df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
            else:
                final_df = df.drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
            
            final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"已成功更新，目前總共累積 {len(final_df)} 筆不重複的期別資料。")
        else:
            print("未抓取到任何 7 位數字，請檢查網站內容。")
            
    except Exception as e:
        print(f"執行時發生錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
