import pyautogui
import pygetwindow as gw
import pytesseract
import cv2
import numpy as np
import re
import time
import keyboard
import pandas as pd
import os
from datetime import datetime

# 設定 Tesseract 路徑
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_region():
    print("【設定模式】")
    print("請將滑鼠移到表格【左上角】，按 F9 記錄...")
    keyboard.wait('f9')
    x1, y1 = pyautogui.position()
    print(f"已記錄左上角: {x1}, {y1}")
    
    print("請將滑鼠移到表格【右下角】，按 F9 記錄...")
    time.sleep(0.5)
    keyboard.wait('f9')
    x2, y2 = pyautogui.position()
    print(f"已記錄右下角: {x2}, {y2}")
    
    return (x1, y1, x2 - x1, y2 - y1)

def save_to_excel(numbers):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(current_dir, "data.xlsx")
    
    sheet_name = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # 假設解析出的第一個數字是期數
    current_draw_id = numbers[0] if numbers else None
    
    # 確保資料結構：時間、期數、號碼1-20
    data_row = [timestamp] + (numbers + [None] * 21)[:21]
    columns = ["時間", "期數"] + [f"號碼{i}" for i in range(1, 21)]
    df_new = pd.DataFrame([data_row], columns=columns)
    
    # 檢查重複期數
    if os.path.exists(file_name):
        try:
            existing_df = pd.read_excel(file_name, sheet_name=sheet_name)
            # 檢查期數欄位中是否已有此期數 (轉換為字串比較)
            if str(current_draw_id) in existing_df["期數"].astype(str).values:
                print(f"[{timestamp}] 期數 {current_draw_id} 已存在，跳過記錄。")
                return
        except Exception:
            pass # 若分頁不存在則繼續執行寫入

    # 寫入 Excel
    if not os.path.exists(file_name):
        df_new.to_excel(file_name, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            try:
                existing_df = pd.read_excel(file_name, sheet_name=sheet_name)
                combined_df = pd.concat([existing_df, df_new], ignore_index=True)
                combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
            except ValueError:
                df_new.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"[{timestamp}] 成功寫入期數 {current_draw_id} 至 Excel")

def main():
    region = get_region()
    print("\n設定完成！")
    print("按下 F10 開始【自動抓取】(每 1 分鐘一次)，按 ESC 停止。")
    
    running = False
    while True:
        if keyboard.is_pressed('f10'):
            running = True
            print(">>> 自動監控模式已啟動...")
        if keyboard.is_pressed('esc'):
            print("程式結束。")
            break
            
        if running:
            screenshot = pyautogui.screenshot(region=region)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
            
            text = pytesseract.image_to_string(thresh, lang='chi_tra+eng', config='--psm 6')
            numbers = re.findall(r'\d+', text)
            
            if numbers:
                save_to_excel(numbers)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 未讀到數字。")
            
            # 修改為 60 秒
            time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[錯誤]: {e}")
        input("按 Enter 關閉...")