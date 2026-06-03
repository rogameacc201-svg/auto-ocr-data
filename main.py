import requests
import time

def debug_scraper():
    URL = f"https://www.pilio.idv.tw/bingo/list.asp?t={int(time.time())}"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9'
    }
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        # 這裡不進行任何處理，直接印出原始資料
        print("--- 原始內容前 500 個字元 (UTF-8 顯示) ---")
        print(response.content[:500])
        
        # 看看 big5 解碼後的結果
        print("\n--- Big5 解碼後前 500 個字元 ---")
        print(response.content.decode('big5', errors='ignore')[:500])
            
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    debug_scraper()
