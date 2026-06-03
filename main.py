import subprocess
import sys

# 自動安裝缺少的套件
def install_requirements():
    required = {'selenium', 'beautifulsoup4', 'pandas'}
    installed = {pkg.key for pkg in __import__('pkg_resources').working_set}
    missing = required - installed
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

install_requirements()

# 現在可以安全匯入
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

def run_scraper():
    print("--- 啟動動態渲染抓取 ---")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # 確保你有安裝 chromedriver，GitHub Actions 預設環境通常已有
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.pilio.idv.tw/bingo/list.asp")
    
    time.sleep(5) 
    html = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    # 解析期別與號碼
    matches = re.findall(r'(\d{9}).*?([\d, \s]{50,})', text)
    
    data = []
    for period, nums_str in matches:
        nums = re.findall(r'\d{2}', nums_str)
        if len(nums) >= 20:
            data.append([period] + nums[:20])
            
    if not data:
        print("未抓到資料，檢查渲染後的文字：")
        print(text[:500])
    else:
        df = pd.DataFrame(data, columns=['期別'] + [f'號碼{i+1}' for i in range(20)])
        df.drop_duplicates(subset=['期別']).to_csv("data.csv", index=False, encoding='utf-8-sig')
        print(f"成功！已儲存 {len(df)} 筆資料。")

if __name__ == "__main__":
    run_scraper()
