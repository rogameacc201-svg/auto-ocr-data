import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def run_scraper():
    print("--- 執行精準結構爬取 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    # 增加完整的 Headers 模擬真實瀏覽器
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.pilio.idv.tw/bingo/list.asp',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        # 強制使用 big5 編碼解析
        response.encoding = 'big5'
        
        # 使用 soup 直接獲取文本
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        # 觀察到目標資料格式類似：期別: 115031154 \n 02, 07, 09...
        # 我們直接尋找 9 位數字的期別
        import re
        # 尋找所有 9 位數字，並提取其後面的 20 個數字
        # 這裡利用 finditer 來處理
        data = []
        # 將內容拆分為多個區塊處理
        blocks = re.split(r':\s*', text)
        
        for block in blocks:
            # 嘗試找出 9 位數字作為期別
            period_match = re.search(r'\d{9}', block)
            if period_match:
                period = period_match.group()
                # 找出區塊內所有的兩位數
                nums = re.findall(r'\b\d{2}\b', block)
                if len(nums) >= 20:
                    data.append([period] + nums[:20])
        
        if not data:
            print("依然無法解析！這代表網站可能已經完全阻擋了這類爬蟲。")
            return

        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        
        # 去重與儲存
        file_path = "data.csv"
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path, dtype={'期別': str})
            df['期別'] = df['期別'].astype(str)
            final_df = pd.concat([df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        else:
            final_df = df.sort_values(by='期別', ascending=False)
            
        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功！已儲存 {len(final_df)} 筆資料。")
            
    except Exception as e:
        print(f"爬取錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
