#!/usr/bin/env python3
"""
直接測試 OpenAI 古風回覆功能的腳本
無需啟動 API 伺服器，直接調用 openai_client 模組
"""

import os
from dotenv import load_dotenv
import sys
import time

# 載入環境變數
load_dotenv()

# 檢查 OpenAI API Key
if not os.getenv("OPENAI_API_KEY"):
    print("錯誤：環境變數 OPENAI_API_KEY 未設置")
    print("請確認您的 .env 文件中包含有效的 OpenAI API Key")
    sys.exit(1)

# 導入古風回覆生成函數
try:
    from utils.openai_client import generate_classical_reply
except ImportError:
    print("錯誤：無法導入 generate_classical_reply 函數")
    print("請確認 utils/openai_client.py 文件存在且包含該函數")
    sys.exit(1)

def print_with_color(text, color="green"):
    """使用顏色打印文字"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    
    color_code = colors.get(color.lower(), colors["reset"])
    print(f"{color_code}{text}{colors['reset']}")

def test_predefined_messages():
    """測試預定義的訊息列表"""
    test_messages = [
        "你好，今天天氣真好！",
        "我最近心情不錯，想出去走走。",
        "這部電影好看嗎？我在考慮要不要去看。",
        "你喜歡喝咖啡嗎？我每天早上都要喝一杯。",
        "討論一下人工智能的發展趨勢吧。"
    ]
    
    print("==== OpenAI 古風回覆功能測試 ====")
    print(f"共測試 {len(test_messages)} 條訊息")
    print("------------------------------")
    
    for i, message in enumerate(test_messages):
        print(f"\n測試 #{i+1}：")
        print(f"原始訊息：{message}")
        
        try:
            # 測量回覆生成時間
            start_time = time.time()
            reply = generate_classical_reply(message)
            end_time = time.time()
            
            print("古風回覆：", end="")
            print_with_color(reply)
            print(f"生成時間：{end_time - start_time:.2f} 秒")
        except Exception as e:
            print_with_color(f"錯誤：{str(e)}", "red")
        
        print("------------------------------")

def interactive_test():
    """互動式測試"""
    print("\n==== 互動式測試 ====")
    print("現在您可以輸入自己的訊息進行測試")
    print("輸入 'exit' 或 'quit' 或按 Ctrl+C 結束測試")
    
    try:
        while True:
            print("\n請輸入您想轉換為古風風格的訊息：")
            user_input = input("> ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("測試結束")
                break
            
            if not user_input.strip():
                print_with_color("請輸入有效的訊息", "yellow")
                continue
            
            try:
                # 測量回覆生成時間
                start_time = time.time()
                reply = generate_classical_reply(user_input)
                end_time = time.time()
                
                print("古風回覆：", end="")
                print_with_color(reply)
                print(f"生成時間：{end_time - start_time:.2f} 秒")
            except Exception as e:
                print_with_color(f"錯誤：{str(e)}", "red")
                print("請檢查 API Key 是否有效或是否達到 API 使用限制")
    except KeyboardInterrupt:
        print("\n測試被中斷")
        print("測試結束")

if __name__ == "__main__":
    print("直接測試 OpenAI 古風回覆功能")
    print("無需啟動 API 伺服器")
    print("=================================\n")
    
    # 測試預定義訊息
    test_predefined_messages()
    
    # 互動式測試
    interactive_test() 