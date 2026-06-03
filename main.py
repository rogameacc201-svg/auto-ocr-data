from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import time

def run_scraper():
    print("--- 啟動動態渲染抓取 ---")
    options = Options()
    options.add_argument("--headless")  # 無頭模式
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # 啟動瀏覽器
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.pilio.idv.tw/bingo/list.asp")
    
    # 給它一點時間載入 JavaScript
    time.sleep(5) 
    
    # 抓取渲染後的完整 HTML
    html = driver.page_source
    driver.quit()
    
    # 解析資料
    # 網站現在的格式可能已經改為更嚴謹的 HTML 表格
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    # 進行更廣泛的搜尋，確保能抓到期別與號碼
    # 尋找 9 位數字後面跟著一串號碼
    matches = re.findall(r'(\d{9}).*?([\d, ]{50,})', text)
    
    data = []
    for period, nums_str in matches:
        nums = re.findall(r'\d{2}', nums_str)
        if len(nums) >= 20:
            data.append([period] + nums[:20])
            
    if not data:
        print("依然失敗，這代表資料可能被寫在特殊的 script 標籤中。")
    else:
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        file_path = "data.csv"
        # 簡單的儲存邏輯
        df.drop_duplicates(subset=['期別']).to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"成功！已從動態網頁抓取 {len(df)} 筆資料。")

if __name__ == "__main__":
    run_scraper()
