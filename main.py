import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

url = "https://www.pilio.idv.tw/bingo/list.asp"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 【修正 1】：改用更底層的 content 處理，強制處理編碼問題
response = requests.get(url, headers=headers, timeout=20)
content = response.content.decode('big5', errors='ignore') 

soup = BeautifulSoup(content, 'html.parser')
text_content = soup.get_text()

# 【修正 2】：放寬 Regex 匹配條件
# 改用：尋找「期別」關鍵字，後面跟著任何數字，再匹配後面的數字序列
# 這能避開「冒號是否為全形」的問題
pattern = re.compile(r'期別[:：]?\s*(\d+)】?\s*([\d\s,]+)')

matches = pattern.findall(text_content)

data = []
for m in matches:
    period = m[0]
    # 清理號碼：只抓出數字，並用空格分開
    numbers = re.findall(r'\d{2}', m[1])
    
    if len(numbers) >= 20:
        data.append([period] + numbers[:20])

if not data:
    print("還是抓不到，請檢查網頁內容：")
    print(text_content[:500]) # 印出片段讓我們分析
else:
    cols = ['期別'] + [f'號碼{i+1}' for i in range(20)]
    df = pd.DataFrame(data, columns=cols)
    df.to_csv("data.csv", index=False, encoding='utf-8-sig')
    print("成功抓取！")
    print(df.head())
