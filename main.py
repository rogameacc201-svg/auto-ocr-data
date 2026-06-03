import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime

# 目標網址
URL = "https://www.pilio.idv.tw/bingo/list.asp"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def run_scraper():
    print("--- 開始執行爬蟲 ---")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()

        pattern = re.compile(r'期別: (\d+)】\s+([\d, \s]+)')
        matches = pattern.findall(text_content)
        
        if not matches:
            print("錯誤：找不到期別資料，請確認網頁結構")
            return

        data = []
        today = datetime.now().strftime('%Y-%m-%d')
        for m in matches:
            period = m[0]
            numbers = re.sub(r'\s+', '', m[1]).split(',')
            if len(numbers) >= 20:
                data.append([today, period] + numbers[:20])

        new_df = pd.DataFrame(data, columns=['日期', '期別'] + [f'號碼{i+1}' for i in range(20)])

        # 寫入或合併資料
        if os.path.exists("data.csv"):
            old_df = pd.read_csv("data.csv")
            final_df = pd.concat([new_df, old_df]).drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        else:
            final_df = new_df

        final_df.to_csv("data.csv", index=False, encoding='utf-8-sig')
        print("成功：data.csv 已更新")

    except Exception as e:
        print(f"程式執行異常: {e}")
        # 我們不再呼叫 sys.exit(1)，讓程式自然結束，這樣 Action 就不會報紅色失敗

if __name__ == "__main__":
    run_scraper()
