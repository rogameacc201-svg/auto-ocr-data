from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

def run_scraper():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # 明確指定使用系統安裝的 chromium
    options.binary_location = "/usr/bin/chromium"
    
    # 初始化 WebDriver
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.pilio.idv.tw/bingo/list.asp")
        time.sleep(5) 
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text = soup.get_text()
    finally:
        driver.quit()
    
    # 解析數據...
    matches = re.findall(r'(\d{9}).*?([\d, \s]{50,})', text)
    data = []
    for period, nums_str in matches:
        nums = re.findall(r'\d{2}', nums_str)
        if len(nums) >= 20:
            data.append([period] + nums[:20])
            
    if data:
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        df['日期'] = df['期別'].apply(lambda x: f"20{x[1:3]}/{x[3:5]}/{x[5:7]}")
        df.to_csv("data.csv", index=False, encoding='utf-8-sig')
        print(f"成功儲存 {len(df)} 筆資料。")

if __name__ == "__main__":
    run_scraper()
