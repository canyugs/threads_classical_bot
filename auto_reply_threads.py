#!/usr/bin/env python3
import argparse
import time
import json
import requests
from datetime import datetime, timedelta
from utils.list_threads_posts import get_user_threads_posts, get_thread_post_details, get_threads_user_id
from utils.openai_client import generate_classical_reply
from utils.threads_api import create_reply_with_two_steps

def fetch_post_replies(post_id):
    """
    獲取指定貼文下的所有回覆
    
    Args:
        post_id: 貼文 ID
    
    Returns:
        回覆列表或失敗時返回 None
    """
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
    url = f"https://graph.threads.net/v1.0/{post_id}/replies"
    params = {
        "access_token": THREADS_ACCESS_TOKEN,
        "limit": 50,  # 最多獲取 50 條回覆
        "fields": "id,text,timestamp,from{id,username,name}"
    }
    
    response = requests.get(url, params=params)
    if not response.ok:
        return {"error": f"獲取回覆列表失敗: {response.text}"}
    
    return response.json()

def format_timestamp(timestamp_str):
    """將 ISO 格式的時間戳轉換為易讀格式"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str

def parse_timestamp(timestamp_str):
    """將 ISO 格式的時間戳轉換為 datetime 對象"""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        return None

def check_if_replied_by_me(replies_data, my_user_id, verbose=True):
    """
    檢查留言者是否已被我回覆過
    
    Args:
        replies_data: 回覆數據
        my_user_id: 我的用戶 ID
        verbose: 是否顯示詳細日誌
    
    Returns:
        已回覆的用戶 ID 集合
    """
    replied_users = set()
    my_replies = []
    
    # 先獲取所有留言者
    all_commenters = {}
    
    if "data" in replies_data:
        for reply in replies_data["data"]:
            user_info = reply.get("from", {})
            user_id = user_info.get("id")
            if user_id:
                all_commenters[user_id] = {
                    "username": user_info.get("username", "未知用戶"),
                    "name": user_info.get("name", "未知名稱"),
                    "text": reply.get("text", "[無文字內容]"),
                    "timestamp": reply.get("timestamp", "")
                }
    
    # 找出我的所有回覆
    if "data" in replies_data:
        for reply in replies_data["data"]:
            # 如果是我發的回覆
            if reply.get("from", {}).get("id") == my_user_id:
                my_replies.append({
                    "id": reply.get("id"),
                    "text": reply.get("text", "[無文字內容]"),
                    "timestamp": reply.get("timestamp", "")
                })
    
    if verbose and my_replies:
        print(f"\n🔍 在此貼文下找到你的 {len(my_replies)} 條回覆:")
        for idx, reply in enumerate(my_replies, 1):
            timestamp = format_timestamp(reply["timestamp"])
            print(f"  {idx}. 時間: {timestamp}")
            print(f"     內容: {reply['text'][:50]}{'...' if len(reply['text']) > 50 else ''}")
    
    # 簡化處理：假設所有其他用戶都被回覆過
    if my_replies:
        for user_id, user_info in all_commenters.items():
            if user_id != my_user_id:
                replied_users.add(user_id)
    
    if verbose and replied_users:
        print(f"\n✅ 被視為已回覆的用戶: {len(replied_users)} 位")
        for user_id in replied_users:
            user_info = all_commenters.get(user_id, {})
            username = user_info.get("username", "未知用戶")
            name = user_info.get("name", "未知名稱")
            print(f"  - {name} (@{username})")
    
    return replied_users

def auto_reply_to_post(post_id, max_replies=None, days=None, dry_run=False, verbose=True):
    """
    自動回覆指定貼文下尚未回覆的留言
    
    Args:
        post_id: 貼文 ID
        max_replies: 最多回覆幾條留言 (None 表示不限制)
        days: 只回覆最近幾天內的留言 (None 表示不限制)
        dry_run: 是否只模擬執行，不實際發送回覆
        verbose: 是否顯示詳細日誌
    """
    print(f"正在處理貼文 ID: {post_id}")
    
    # 獲取我的用戶 ID
    my_user_id = get_threads_user_id()
    if not my_user_id:
        print("❌ 無法獲取你的 Threads 用戶 ID")
        return
    
    # 獲取貼文詳細資訊
    post_details = get_thread_post_details(post_id)
    if "error" in post_details:
        print(f"❌ 獲取貼文詳細資訊失敗: {post_details['error']}")
        return
    
    post_text = post_details.get("text", "[無文字內容]")
    print(f"📝 貼文內容: {post_text}")
    
    # 獲取貼文下的所有回覆
    replies = fetch_post_replies(post_id)
    if "error" in replies:
        print(f"❌ 獲取回覆列表失敗: {replies['error']}")
        return
    
    if "data" not in replies or not replies["data"]:
        print("ℹ️ 該貼文下沒有任何回覆")
        return
    
    print(f"🔍 找到 {len(replies['data'])} 條回覆")
    
    # 檢查哪些用戶已被回覆過
    replied_users = check_if_replied_by_me(replies, my_user_id, verbose)
    print(f"✓ 已回覆過 {len(replied_users)} 位用戶")
    
    # 計算日期限制
    date_limit = None
    if days is not None:
        date_limit = datetime.now() - timedelta(days=days)
        print(f"📅 只回覆 {format_timestamp(date_limit.isoformat())} 之後的留言")
    
    # 遍歷所有回覆，找出尚未回覆的留言
    replies_to_answer = []
    
    for reply in replies["data"]:
        user_info = reply.get("from", {})
        user_id = user_info.get("id")
        
        # 跳過自己的留言和已回覆過的用戶
        if user_id == my_user_id or user_id in replied_users:
            continue
        
        # 檢查日期限制
        if date_limit:
            reply_time = parse_timestamp(reply.get("timestamp", ""))
            if reply_time and reply_time < date_limit:
                if verbose:
                    print(f"⏱️ 跳過較早的留言: {reply.get('text', '')[:30]}... ({format_timestamp(reply.get('timestamp', ''))})")
                continue
        
        username = user_info.get("username", "未知用戶")
        name = user_info.get("name", "未知名稱")
        text = reply.get("text", "[無文字內容]")
        reply_id = reply.get("id")
        timestamp = format_timestamp(reply.get("timestamp", ""))
        
        replies_to_answer.append({
            "reply_id": reply_id,
            "user_id": user_id,
            "username": username,
            "name": name,
            "text": text,
            "timestamp": timestamp
        })
    
    # 限制回覆數量
    if max_replies is not None and len(replies_to_answer) > max_replies:
        print(f"⚠️ 符合條件的留言有 {len(replies_to_answer)} 條，根據設置將只回覆前 {max_replies} 條")
        replies_to_answer = replies_to_answer[:max_replies]
    
    print(f"📨 找到 {len(replies_to_answer)} 條需要回覆的留言")
    
    # 處理需要回覆的留言
    for idx, reply_info in enumerate(replies_to_answer, 1):
        print(f"\n--- 正在處理第 {idx}/{len(replies_to_answer)} 條留言 ---")
        print(f"👤 用戶: {reply_info['name']} (@{reply_info['username']})")
        print(f"💬 內容: {reply_info['text']}")
        print(f"⏰ 時間: {reply_info['timestamp']}")
        
        # 使用 OpenAI 生成文言文回覆
        print("🤖 正在生成古風回覆...")
        reply_text = generate_classical_reply(reply_info['text'])
        print(f"✍️ 生成的回覆: {reply_text}")
        
        if not dry_run:
            # 發送回覆
            print("📤 正在發送回覆...")
            result = create_reply_with_two_steps(
                threads_user_id=my_user_id,
                reply_to_id=reply_info['reply_id'],
                text=reply_text
            )
            
            if result:
                print("✅ 回覆成功發送!")
            else:
                print("❌ 回覆發送失敗")
            
            # 為避免 API 限制，等待數秒再繼續
            if idx < len(replies_to_answer):
                print("⏳ 等待 10 秒後處理下一條...")
                time.sleep(10)
        else:
            print("🔄 模擬模式: 未實際發送回覆")
    
    print("\n✅ 所有留言處理完成!")

def auto_reply_all_posts(count=5, max_replies=None, days=None, dry_run=False, verbose=True):
    """
    自動回覆最近幾篇貼文下的所有尚未回覆的留言
    
    Args:
        count: 處理的貼文數量
        max_replies: 每篇貼文最多回覆幾條留言 (None 表示不限制)
        days: 只回覆最近幾天內的留言 (None 表示不限制)
        dry_run: 是否只模擬執行，不實際發送回覆
        verbose: 是否顯示詳細日誌
    """
    print(f"🔍 正在獲取最近 {count} 篇貼文...")
    
    # 獲取最近的貼文
    posts_result = get_user_threads_posts(limit=count)
    if "error" in posts_result:
        print(f"❌ 獲取貼文列表失敗: {posts_result['error']}")
        return
    
    if "data" not in posts_result or not posts_result["data"]:
        print("❌ 沒有找到任何貼文")
        return
    
    posts = posts_result["data"]
    print(f"✓ 找到 {len(posts)} 篇貼文")
    
    # 遍歷所有貼文，處理回覆
    for idx, post in enumerate(posts, 1):
        post_id = post.get("id", "未知")
        text = post.get("text", "[無文字內容]")
        post_time = format_timestamp(post.get("timestamp", ""))
        
        print(f"\n==== 處理第 {idx}/{len(posts)} 篇貼文 ====")
        print(f"ID: {post_id}")
        print(f"時間: {post_time}")
        print(f"內容: {text}")
        
        # 處理這篇貼文下的回覆
        auto_reply_to_post(post_id, max_replies, days, dry_run, verbose)
        
        # 為避免 API 限制，等待數秒再繼續
        if idx < len(posts):
            print("⏳ 等待 15 秒後處理下一篇貼文...")
            time.sleep(15)
    
    print("\n🎉 所有貼文處理完成!")

def main():
    parser = argparse.ArgumentParser(description="自動回覆 Threads 貼文下的留言")
    
    # 建立子命令
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 處理單一貼文的子命令
    post_parser = subparsers.add_parser("post", help="處理特定貼文下的留言")
    post_parser.add_argument("post_id", help="要處理的貼文 ID")
    post_parser.add_argument("-n", "--num", type=int, help="最多回覆幾條留言")
    post_parser.add_argument("-d", "--dry-run", action="store_true", help="僅模擬執行，不實際發送回覆")
    post_parser.add_argument("-v", "--verbose", action="store_true", default=True, help="顯示詳細的檢測資訊")
    post_parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", help="不顯示詳細的檢測資訊")
    post_parser.add_argument("--days", type=int, help="只回覆最近幾天內的留言")
    
    # 處理多篇貼文的子命令
    posts_parser = subparsers.add_parser("posts", help="處理多篇貼文下的留言")
    posts_parser.add_argument("-c", "--count", type=int, default=5, help="要處理的貼文數量 (預設: 5)")
    posts_parser.add_argument("-n", "--num", type=int, help="每篇貼文最多回覆幾條留言")
    posts_parser.add_argument("-d", "--dry-run", action="store_true", help="僅模擬執行，不實際發送回覆")
    posts_parser.add_argument("-v", "--verbose", action="store_true", default=True, help="顯示詳細的檢測資訊")
    posts_parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", help="不顯示詳細的檢測資訊")
    posts_parser.add_argument("--days", type=int, help="只回覆最近幾天內的留言")
    
    args = parser.parse_args()
    
    if args.command == "post":
        auto_reply_to_post(args.post_id, args.num, args.days, args.dry_run, args.verbose)
    elif args.command == "posts":
        auto_reply_all_posts(args.count, args.num, args.days, args.dry_run, args.verbose)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 