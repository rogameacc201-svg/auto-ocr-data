import pandas as pd
import shutil
import time
import os

# 自動獲取此腳本所在的資料夾路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(BASE_DIR, 'data.xlsx')
TEMP_FILE = os.path.join(BASE_DIR, 'temp_copy.xlsx')
JSON_FILE = os.path.join(BASE_DIR, 'data.json')

def process_data():
    try:
        # 檢查原始檔案是否存在
        if os.path.exists(SOURCE_FILE):
            # 複製檔案 (避開原始檔案被其他程式鎖定的問題)
            shutil.copyfile(SOURCE_FILE, TEMP_FILE)
            
            # 讀取副本並轉為 JSON
            df = pd.read_excel(TEMP_FILE, engine='openpyxl')
            df.to_json(JSON_FILE, orient='records', force_ascii=False, indent=4)
            print(f"[{time.ctime()}] 成功！數據已更新至 data.json")
        else:
            print(f"[{time.ctime()}] 錯誤：找不到檔案 {SOURCE_FILE}，請確認名稱是否正確")
            
    except Exception as e:
        print(f"[{time.ctime()}] 讀取中... (原始程式可能正在寫入檔案: {e})")

# 主程式
if __name__ == "__main__":
    print(f"程式已啟動！")
    print(f"監控目錄: {BASE_DIR}")
    print("---")
    
    while True:
        process_data()
        time.sleep(60) # 每 60 秒循環一次