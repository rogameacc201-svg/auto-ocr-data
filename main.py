import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import time

def convert_period_to_date(period_str):
    # 根據期別 115031154 轉換為 2026/03/11
    # 115年 + 1911 = 2026
    try:
        y = int(period_str[:3]) + 1911
        m = period_str[3:5]
        d = period_str[5:7]
        return f"{y}/{m}/{d}"
    except:
        return "2026/06/03" # 預設值

def run_scraper():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.pilio.idv.tw/bingo/list.asp")
    time.sleep(5) 
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    text = soup.get_text()
    driver.quit()
    
    matches = re.findall(r'(\d{9}).*?([\d, \s]{50,})', text)
    data = []
    for period, nums_str in matches:
        nums = re.findall(r'\d{2}', nums_str)
        if len(nums) >= 20:
            data.append([period] + nums[:20])
            
    if data:
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        df['日期'] = df['期別'].apply(convert_period_to_date)
        # 調整順序，日期放最前
        cols = ['日期', '期別'] + [f'號碼{i+1}' for i in range(20)]
        df = df[cols].drop_duplicates(subset=['期別']).sort_values(by='期別', ascending=False)
        df.to_csv("data.csv", index=False, encoding='utf-8-sig')
        print(f"成功儲存 {len(df)} 筆資料。")

if __name__ == "__main__":
    run_scraper()
