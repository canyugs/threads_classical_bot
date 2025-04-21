import requests
import os
import json
import time
from fastapi import FastAPI, Request
from utils.openai_client import generate_classical_reply
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# 使用 .env 檔案中的 THREADS_ACCESS_TOKEN
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
app = FastAPI()

def create_threads_media_container(threads_user_id: str, media_type: str, text: str, link_attachment: str = None, image_url: str = None, video_url: str = None, reply_to_id: str = None):
    """
    第一步：使用 Threads API 建立媒體容器（可用於發文或回覆）
    
    Args:
        threads_user_id: Threads 使用者 ID
        media_type: 媒體類型 (TEXT, IMAGE, VIDEO)
        text: 貼文文字內容
        link_attachment: 連結附件 (僅適用於文字貼文)
        image_url: 圖片 URL (僅適用於圖片貼文)
        video_url: 影片 URL (僅適用於影片貼文)
        reply_to_id: 要回覆的貼文或回覆 ID
    
    Returns:
        容器 ID 或失敗時返回 None
    """
    url = f"https://graph.threads.net/v1.0/{threads_user_id}/threads"
    
    # 建立資料字典
    data = {
        "media_type": media_type,
        "text": text,
        "access_token": THREADS_ACCESS_TOKEN
    }
    
    # 根據媒體類型添加特定參數
    if media_type == "IMAGE" and image_url:
        data["image_url"] = image_url
    elif media_type == "VIDEO" and video_url:
        data["video_url"] = video_url
    
    # 添加連結附件 (僅適用於文字貼文)
    if media_type == "TEXT" and link_attachment:
        data["link_attachment"] = link_attachment
    
    # 如果是回覆，添加 reply_to_id 參數
    if reply_to_id:
        data["reply_to_id"] = reply_to_id
    
    response = requests.post(url, data=data)
    if not response.ok:
        print(f"媒體容器建立失敗: {response.text}")
        return None
    
    return response.json().get("id")

def publish_threads_container(threads_user_id: str, creation_id: str):
    """
    第二步：使用 Threads API 發佈媒體容器（用於發文或回覆）
    
    Args:
        threads_user_id: Threads 使用者 ID
        creation_id: 媒體容器 ID
    
    Returns:
        發佈的貼文 ID 或失敗時返回 None
    """
    url = f"https://graph.threads.net/v1.0/{threads_user_id}/threads_publish"
    data = {
        "creation_id": creation_id,
        "access_token": THREADS_ACCESS_TOKEN
    }
    
    response = requests.post(url, data=data)
    if not response.ok:
        print(f"容器發佈失敗: {response.text}")
        return None
    
    return response.json()

def create_post_with_two_steps(threads_user_id: str, text: str, media_type: str = "TEXT", link_attachment: str = None, image_url: str = None, video_url: str = None):
    """
    使用兩步驟流程創建並發布貼文（符合官方 API 文檔）
    
    Args:
        threads_user_id: Threads 使用者 ID
        text: 貼文文字內容
        media_type: 媒體類型，預設為 TEXT
        link_attachment: 連結附件 (僅適用於文字貼文)
        image_url: 圖片 URL (僅適用於圖片貼文)
        video_url: 影片 URL (僅適用於影片貼文)
    
    Returns:
        發佈的貼文 ID 或失敗時返回 None
    """
    # 步驟 1: 創建媒體容器
    container_id = create_threads_media_container(
        threads_user_id=threads_user_id,
        media_type=media_type,
        text=text,
        link_attachment=link_attachment,
        image_url=image_url,
        video_url=video_url
    )
    
    if not container_id:
        print("媒體容器創建失敗")
        return None
    
    # 建議等待一段時間
    time.sleep(5)  # 等待 5 秒讓伺服器處理
    
    # 步驟 2: 發布媒體容器
    result = publish_threads_container(threads_user_id, container_id)
    if not result:
        print("媒體容器發布失敗")
        return None
    
    return result

def create_reply_with_two_steps(threads_user_id: str, reply_to_id: str, text: str, media_type: str = "TEXT"):
    """
    使用兩步驟流程創建並發布回覆（符合官方 API 文檔）
    
    Args:
        threads_user_id: Threads 使用者 ID
        reply_to_id: 要回覆的貼文或回覆 ID
        text: 回覆文字內容
        media_type: 媒體類型，預設為 TEXT
    
    Returns:
        發佈的回覆 ID 或失敗時返回 None
    """
    # 步驟 1: 創建回覆容器
    container_id = create_threads_media_container(
        threads_user_id=threads_user_id,
        media_type=media_type,
        text=text,
        reply_to_id=reply_to_id
    )
    
    if not container_id:
        print("回覆容器創建失敗")
        return None
    
    # 建議等待一段時間
    time.sleep(5)  # 等待 5 秒讓伺服器處理
    
    # 步驟 2: 發布回覆容器
    result = publish_threads_container(threads_user_id, container_id)
    if not result:
        print("回覆容器發布失敗")
        return None
    
    return result

@app.post("/api/webhook")
async def handle_event(request: Request):
    """處理 Threads API 的 Webhook 回調"""
    body = await request.json()
    print(json.dumps(body, indent=2))

    # Threads Webhook 格式處理
    # 參考: https://developers.facebook.com/docs/threads/webhooks
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") == "threads":
                value = change.get("value", {})
                if "replies" in value:
                    # 處理回覆通知
                    reply_data = value.get("replies", {})
                    thread_id = reply_data.get("thread_id")
                    text = reply_data.get("text", "")
                    from_user = reply_data.get("from", {})
                    threads_user_id = from_user.get("id")
                    
                    if text and thread_id and threads_user_id:
                        # 避免回覆自己的訊息
                        my_user_id = get_threads_user_id()
                        if threads_user_id != my_user_id:
                            # 使用 OpenAI 來生成古風回覆
                            reply_text = generate_classical_reply(text)
                            
                            # 使用兩步驟回覆流程
                            create_reply_with_two_steps(
                                threads_user_id=my_user_id,
                                reply_to_id=thread_id,
                                text=reply_text
                            )

    return {"status": "ok"}

def get_threads_user_id():
    """獲取 Threads 使用者 ID"""
    url = f"https://graph.threads.net/v1.0/me?fields=id&access_token={THREADS_ACCESS_TOKEN}"
    response = requests.get(url)
    if response.ok:
        return response.json().get("id")
    return None

# 添加測試 OpenAI 古風回覆生成的 API 端點
@app.post("/api/test-openai")
async def test_openai_generation(request: Request):
    """測試 OpenAI 古風回覆生成功能"""
    body = await request.json()
    message = body.get("message", "")
    if not message:
        return {"error": "請提供要轉換為古風風格的訊息"}
    
    try:
        reply = generate_classical_reply(message)
        return {
            "original": message,
            "reply": reply,
            "success": True
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "error": f"生成古風回覆失敗: {str(e)}",
            "details": error_details,
            "success": False
        }

# 以下是為了通過 API 測試所需的端點

@app.get("/api/threads-user-id")
async def get_user_id_endpoint():
    """獲取 Threads 使用者 ID (直接返回用戶 ID)"""
    user_id = get_threads_user_id()
    if user_id:
        return user_id
    return {"error": "找不到 Threads 帳號"}

@app.get("/api/threads-user-info")
async def get_user_info():
    """獲取 Threads 帳號資訊 (threads_basic)"""
    url = f"https://graph.threads.net/v1.0/me?fields=id,username,name,threads_profile_picture_url,threads_biography&access_token={THREADS_ACCESS_TOKEN}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return {"error": "無法獲取 Threads 帳號資訊"}

@app.get("/api/threads-post-limit")
async def fetch_threads_post_limit():
    """檢查 Threads 發文限制 (threads_content_publish)"""
    threads_user_id = get_threads_user_id()
    if not threads_user_id:
        return {"error": "找不到 Threads 帳號"}
    
    url = f"https://graph.threads.net/v1.0/{threads_user_id}/threads_publishing_limit?fields=quota_usage,config&access_token={THREADS_ACCESS_TOKEN}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return {"error": "無法獲取發文限制"}

@app.get("/api/threads-mentions")
async def get_threads_mentions():
    """獲取 Threads 提及 (threads_manage_mentions)"""
    threads_user_id = get_threads_user_id()
    if not threads_user_id:
        return {"error": "找不到 Threads 帳號"}
    
    url = f"https://graph.threads.net/v1.0/{threads_user_id}/mentions?access_token={THREADS_ACCESS_TOKEN}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return {"error": "無法獲取提及資訊"}

@app.get("/api/threads-replies")
async def get_threads_replies():
    """獲取 Threads 回覆 (threads_read_replies)"""
    threads_user_id = get_threads_user_id()
    if not threads_user_id:
        return {"error": "找不到 Threads 帳號"}
    
    url = f"https://graph.threads.net/v1.0/{threads_user_id}/replies?access_token={THREADS_ACCESS_TOKEN}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    return {"error": "無法獲取回覆資訊"}

@app.post("/api/threads")
async def create_media_container_endpoint(request: Request):
    """第一步：建立 Threads 媒體容器 (符合官方 API)"""
    body = await request.json()
    media_type = body.get("media_type", "TEXT")
    text = body.get("text", "")
    link_attachment = body.get("link_attachment")
    image_url = body.get("image_url")
    video_url = body.get("video_url")
    reply_to_id = body.get("reply_to_id")  # 可用於回覆
    
    if media_type == "TEXT" and not text:
        return {"error": "文字貼文需要提供文字內容"}
    
    if media_type == "IMAGE" and not image_url:
        return {"error": "圖片貼文需要提供圖片 URL"}
    
    if media_type == "VIDEO" and not video_url:
        return {"error": "影片貼文需要提供影片 URL"}
    
    threads_user_id = get_threads_user_id()
    if not threads_user_id:
        return {"error": "找不到 Threads 帳號"}
    
    container_id = create_threads_media_container(
        threads_user_id=threads_user_id,
        media_type=media_type,
        text=text,
        link_attachment=link_attachment,
        image_url=image_url,
        video_url=video_url,
        reply_to_id=reply_to_id
    )
    
    if container_id:
        return {"id": container_id}
    return {"error": "媒體容器建立失敗"}

@app.post("/api/threads-publish")
async def publish_container_endpoint(request: Request):
    """第二步：發佈 Threads 媒體容器 (符合官方 API)"""
    body = await request.json()
    creation_id = body.get("creation_id", "")
    
    if not creation_id:
        return {"error": "缺少媒體容器 ID"}
    
    threads_user_id = get_threads_user_id()
    if not threads_user_id:
        return {"error": "找不到 Threads 帳號"}
    
    result = publish_threads_container(threads_user_id, creation_id)
    if result:
        return result
    return {"error": "媒體容器發佈失敗"}

@app.post("/api/create-post")
async def create_complete_post_endpoint(request: Request):
    """一站式建立貼文 (內部使用兩步驟流程)"""
    body = await request.json()
    text = body.get("text", "")
    media_type = body.get("media_type", "TEXT")
    link_attachment = body.get("link_attachment")
    image_url = body.get("image_url")
    video_url = body.get("video_url")
    
    if not text:
        return {"error": "缺少文字內容"}
    
    threads_user_id = get_threads_user_id()
    if not threads_user_id:
        return {"error": "找不到 Threads 帳號"}
    
    result = create_post_with_two_steps(
        threads_user_id=threads_user_id,
        text=text,
        media_type=media_type,
        link_attachment=link_attachment,
        image_url=image_url,
        video_url=video_url
    )
    
    if result:
        return result
    return {"error": "貼文發佈失敗"}

@app.post("/api/create-reply")
async def create_complete_reply_endpoint(request: Request):
    """一站式建立回覆 (內部使用兩步驟流程)"""
    body = await request.json()
    reply_to_id = body.get("reply_to_id", "")
    text = body.get("text", "")
    media_type = body.get("media_type", "TEXT")
    
    if not reply_to_id:
        return {"error": "缺少要回覆的貼文 ID"}
    
    if not text:
        return {"error": "缺少回覆內容"}
    
    threads_user_id = get_threads_user_id()
    if not threads_user_id:
        return {"error": "找不到 Threads 帳號"}
    
    result = create_reply_with_two_steps(
        threads_user_id=threads_user_id,
        reply_to_id=reply_to_id,
        text=text,
        media_type=media_type
    )
    
    if result:
        return result
    return {"error": "回覆發佈失敗"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


