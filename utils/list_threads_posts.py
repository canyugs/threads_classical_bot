import requests
import os
import json
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# 使用 .env 檔案中的 THREADS_ACCESS_TOKEN
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")

def get_threads_user_id():
    """獲取 Threads 使用者 ID"""
    url = f"https://graph.threads.net/v1.0/me?fields=id&access_token={THREADS_ACCESS_TOKEN}"
    response = requests.get(url)
    if response.ok:
        return response.json().get("id")
    return None

def get_user_threads_posts(limit=25):
    """
    獲取用戶的 Threads 貼文列表
    
    Args:
        limit: 獲取的貼文數量上限，預設為 25
    
    Returns:
        貼文列表或失敗時返回 None
    """
    threads_user_id = get_threads_user_id()
    if not threads_user_id:
        return {"error": "找不到 Threads 帳號"}
    
    url = f"https://graph.threads.net/v1.0/{threads_user_id}/threads"
    params = {
        "access_token": THREADS_ACCESS_TOKEN,
        "limit": limit,
        "fields": "id,text,timestamp,media_type"
    }
    
    response = requests.get(url, params=params)
    if not response.ok:
        return {"error": f"獲取貼文列表失敗: {response.text}"}
    
    return response.json()

def get_thread_post_details(post_id):
    """
    獲取特定 Threads 貼文的詳細資訊
    
    Args:
        post_id: 貼文 ID
    
    Returns:
        貼文詳細資訊或失敗時返回 None
    """
    url = f"https://graph.threads.net/v1.0/{post_id}"
    params = {
        "access_token": THREADS_ACCESS_TOKEN,
        "fields": "id,text,timestamp,media_type"
    }
    
    response = requests.get(url, params=params)
    if not response.ok:
        return {"error": f"獲取貼文詳細資訊失敗: {response.text}"}
    
    return response.json()

if __name__ == "__main__":
    # 測試獲取用戶貼文
    posts = get_user_threads_posts(limit=10)
    print(json.dumps(posts, indent=2))
    
    # 測試獲取特定貼文詳細資訊
    if "data" in posts and len(posts["data"]) > 0:
        post_id = posts["data"][0]["id"]
        post_details = get_thread_post_details(post_id)
        print("\n貼文詳細資訊:")
        print(json.dumps(post_details, indent=2)) 