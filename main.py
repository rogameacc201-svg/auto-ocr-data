import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def run_scraper():
    print("--- 重新定位表格結構 ---")
    URL = "https://www.pilio.idv.tw/bingo/list.asp"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        # 這裡改用 requests 自動檢測編碼，若失敗再手動設為 big5
        response.encoding = 'big5' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尋找頁面上所有的表格列 <tr>
        rows = soup.find_all('tr')
        data = []
        
        for row in rows:
            # 提取每一個格子的文字
            cells = [cell.get_text(strip=True) for cell in row.find_all('td')]
            # 根據經驗，期別+20個號碼通常會佔用 21 個以上的格子
            if len(cells) >= 21:
                # 假設 cells[0] 是期別，cells[1:21] 是號碼
                data.append(cells[:21])
        
        if not data:
            print("無法抓到表格資料，網站可能沒有使用傳統 <table> 標籤。")
            return

        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        
        # 存檔邏輯
        file_path = "data.csv"
        if os.path.exists(file_path):
            old_df = pd.read_csv(file_path)
            final_df = pd.concat([df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        else:
            final_df = df
        
        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功！已抓取 {len(final_df)} 筆完整資料。")
            
    except Exception as e:
        print(f"執行時發生錯誤: {e}")

if __name__ == "__main__":
    run_scraper()
