import os
import csv
from datetime import datetime

def save_data_to_csv(new_data):
    """
    new_data 應該是一個字典，例如:
    {'期別': '115031263', '號碼1': '01', '號碼2': '05', ...}
    """
    file_path = 'data.csv'
    # 取得當前台北時間的日期 (YYYY/MM/DD)
    today = datetime.now().strftime("%Y/%m/%d")
    
    # 將日期加入資料字典
    new_data['日期'] = today
    
    # 定義所有欄位順序 (確保 CSV 格式整齊)
    fieldnames = ['日期', '期別'] + [f'號碼{i}' for i in range(1, 21)]
    
    # 檢查檔案是否存在
    file_exists = os.path.isfile(file_path)
    
    # 【關鍵點】使用 'a' 模式 (Append)，這會將新資料加在檔案最後面，不會蓋掉舊資料
    with open(file_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # 如果是第一次建立檔案，才寫入標題
        if not file_exists:
            writer.writeheader()
        
        # 寫入這筆新的資料
        writer.writerow(new_data)
        
    print(f"成功追加資料: {new_data['期別']} 到 {today}")

# --- 使用範例 ---
# 假設這是你從網頁 OCR 抓到的新一期資料
# 記得要把所有號碼補齊到 20 個
latest_row = {
    '期別': '115031263',
    '號碼1': '01', '號碼2': '05', '號碼3': '06', '號碼4': '13', '號碼5': '19',
    '號碼6': '23', '號碼7': '26', '號碼8': '36', '號碼9': '39', '號碼10': '44',
    '號碼11': '47', '號碼12': '51', '號碼13': '53', '號碼14': '54', '號碼15': '55',
    '號碼16': '62', '號碼17': '64', '號碼18': '68', '號碼19': '77', '號碼20': '80'
}

save_data_to_csv(latest_row)
