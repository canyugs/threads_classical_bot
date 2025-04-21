from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import os
import json
from utils.openai_client import generate_classical_reply
from utils.threads_api import create_reply_with_two_steps, get_threads_user_id

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
@app.get("/api/webhook")
async def verify(request: Request):
    params = dict(request.query_params)
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(content=params.get("hub.challenge"))
    return PlainTextResponse(content="Invalid token", status_code=403)

@app.post("/api/webhook")
async def handle_event(request: Request):
    body = await request.json()
    print(f"接收到 webhook: {json.dumps(body, ensure_ascii=False)}")
    
    # 處理傳統 entry/changes 結構
    if "entry" in body:
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                message = value.get("text", "")
                reply_id = value.get("id", "")
                if message and reply_id:
                    # 使用 OpenAI 生成古風回覆文本
                    reply_text = generate_classical_reply(message)
                    
                    # 獲取自己的 Threads 使用者 ID
                    my_user_id = get_threads_user_id()
                    if my_user_id:
                        # 使用標準兩步驟流程進行回覆
                        result = create_reply_with_two_steps(
                            threads_user_id=my_user_id,
                            reply_to_id=reply_id,
                            text=reply_text
                        )
                        print(f"回覆結果: {result}")
    
    # 處理 values/value 結構 (新結構)
    elif "values" in body and "value" in body.get("values", {}):
        value = body.get("values", {}).get("value", {})
        message = value.get("text", "")
        reply_id = value.get("id", "")
        username = value.get("username", "未知用戶")
        timestamp = value.get("timestamp", "未知時間")
        
        print(f"接收到來自 @{username} 的留言: {message}")
        print(f"留言時間: {timestamp}")
        
        if message and reply_id:
            # 使用 OpenAI 生成古風回覆文本
            reply_text = generate_classical_reply(message)
            
            # 獲取自己的 Threads 使用者 ID
            my_user_id = get_threads_user_id()
            if my_user_id:
                # 使用標準兩步驟流程進行回覆
                result = create_reply_with_two_steps(
                    threads_user_id=my_user_id,
                    reply_to_id=reply_id,
                    text=reply_text
                )
                print(f"回覆結果: {result}")
    
    return {"status": "ok"}