import requests
import re
import pandas as pd
import os

def run_scraper():
    print("--- 執行最終暴力抓取 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        # 用 big5 解碼並忽略亂碼，確保內容完整
        content = response.content.decode('big5', errors='ignore')
        
        # 移除所有換行與過多空格，讓網頁變回單行字串
        clean_content = re.sub(r'[\r\n\s]+', ' ', content)
        
        # 尋找模式：冒號 + 9位數字期別 + (忽略中間可能有的亂碼與符號) + 20個兩位數字
        # 這個正規表達式更強大，它會忽略期別與號碼之間所有的雜訊
        pattern = re.compile(r':\s*(\d{9}).*?(\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2}[, ]{1,2}\d{2})')
        
        matches = pattern.findall(clean_content)
        
        data = []
        for period, nums_str in matches:
            nums = re.findall(r'\d{2}', nums_str)
            if len(nums) >= 20:
                data.append([period] + nums[:20])
        
        if not data:
            print("還是匹配不到！")
            print("--- 網頁內容預覽 (用於除錯) ---")
            print(clean_content[500:1500]) # 印出中段內容讓我們觀察結構
            return

        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        
        # 存檔處理
        file_path = "data.csv"
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path, dtype={'期別': str})
            df['期別'] = df['期別'].astype(str)
            final_df = pd.concat([df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        else:
            final_df = df.sort_values(by='期別', ascending=False)
            
        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功！本次抓到 {len(data)} 期，累積總數 {len(final_df)} 期。")
            
    except Exception as e:
        print(f"執行錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
