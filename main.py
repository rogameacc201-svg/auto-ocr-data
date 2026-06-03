import requests
import re
import pandas as pd
import os

def run_scraper():
    print("--- 開始全面抓取期別與號碼 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        # 用 ignore 處理亂碼
        content = response.content.decode('big5', errors='ignore')
        
        # 【核心邏輯】：這裡假設結構為「期別(7碼) + 號碼群(包含20個數字)」
        # 由於網頁混亂，我們直接抓取一整段包含期別與號碼的文字區塊
        # 假設網頁上期別後接號碼的格式，我們用一組正規表達式來提取
        # 這裡需要你觀察輸出的「片段」來調整 pattern
        
        # 抓取範例：找 7 碼期別，後面跟著 20 個數字
        # 這裡會找出所有期別開頭的段落
        matches = re.findall(r'(\d{7})[\s\S]{0,100}?(\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2}[,\s]+\d{2})', content)
        
        if not matches:
            print("警告: 無法直接抓取號碼結構，請檢查網頁是否有 JavaScript 渲染")
            return

        # 整理成 DataFrame
        data = []
        for m in matches:
            period = m[0]
            # 將號碼字串分割成 list
            nums = re.findall(r'\d{2}', m[1])
            if len(nums) >= 20:
                data.append([period] + nums[:20])
        
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        
        file_path = "data.csv"
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path)
            # 確保型態統一為字串避免比較錯誤
            df['期別'] = df['期別'].astype(str)
            old_df['期別'] = old_df['期別'].astype(str)
            final_df = pd.concat([df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        else:
            final_df = df.sort_values(by='期別', ascending=False)
        
        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功更新，目前總共累積 {len(final_df)} 筆完整資料。")
            
    except Exception as e:
        print(f"執行時發生錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
