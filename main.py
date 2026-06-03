import requests
import re
import pandas as pd
import os
import time

def run_scraper():
    # 增加隨機參數防止快取
    URL = f"https://www.pilio.idv.tw/bingo/list.asp?t={int(time.time())}"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        content = response.content.decode('big5', errors='ignore')
        
        # 進行分塊解析，這能確保不遺漏任何期別
        data = []
        # 以冒號分割，尋找期別與號碼
        blocks = re.split(r':\s*', content)
        
        for block in blocks:
            # 尋找 9 位數期別
            period_match = re.search(r'\d{9}', block)
            if period_match:
                period = period_match.group()
                # 尋找 20 個兩位數號碼
                nums = re.findall(r'\b\d{2}\b', block)
                if len(nums) >= 20:
                    data.append([period] + nums[:20])
        
        if not data:
            print("警告：本次未抓到資料。")
            return

        # 整理成 DataFrame
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        
        # 合併舊檔案 (如果存在的話)
        file_path = "data.csv"
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path, dtype={'期別': str})
            final_df = pd.concat([df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        else:
            final_df = df.sort_values(by='期別', ascending=False)
            
        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功更新！目前總計 {len(final_df)} 筆資料，最新期別為 {final_df.iloc[0]['期別']}")
            
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
