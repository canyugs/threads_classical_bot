import uvicorn
from fastapi import FastAPI
from utils.threads_api import app
from api.list_posts import router as posts_router

# 添加新的路由器
app.include_router(posts_router, prefix="/api")

if __name__ == "__main__":
    print("正在啟動 Threads 古風回覆機器人伺服器...")
    print("API 端點:")
    print("- GET /api/threads-posts?limit=10：列出自己的貼文")
    print("- GET /api/threads-post/{post_id}：查看特定貼文的詳細資訊")
    uvicorn.run(app, host="0.0.0.0", port=8000) 