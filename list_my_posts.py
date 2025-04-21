#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from utils.list_threads_posts import get_user_threads_posts, get_thread_post_details

def format_timestamp(timestamp_str):
    """將 ISO 格式的時間戳轉換為易讀格式"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str

def list_posts(count=10, format_json=False):
    """列出用戶的 Threads 貼文"""
    print(f"正在獲取最近 {count} 篇貼文...\n")
    
    result = get_user_threads_posts(limit=count)
    if "error" in result:
        print(f"錯誤: {result['error']}")
        return
    
    if format_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    
    if "data" not in result or not result["data"]:
        print("沒有找到任何貼文")
        return
    
    posts = result["data"]
    print(f"找到 {len(posts)} 篇貼文：\n")
    
    for i, post in enumerate(posts, 1):
        post_id = post.get("id", "未知")
        text = post.get("text", "[無文字內容]")
        time = format_timestamp(post.get("timestamp", ""))
        media_type = post.get("media_type", "TEXT")
        
        print(f"---- 貼文 {i} ----")
        print(f"ID: {post_id}")
        print(f"時間: {time}")
        print(f"內容: {text}")
        print(f"媒體類型: {media_type}")
        print()

def show_post_details(post_id, format_json=False):
    """顯示特定 Threads 貼文的詳細資訊"""
    print(f"正在獲取貼文 ID: {post_id} 的詳細資訊...\n")
    
    result = get_thread_post_details(post_id)
    if "error" in result:
        print(f"錯誤: {result['error']}")
        return
    
    if format_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    
    post = result
    text = post.get("text", "[無文字內容]")
    time = format_timestamp(post.get("timestamp", ""))
    media_type = post.get("media_type", "TEXT")
    
    print(f"---- 貼文詳細資訊 ----")
    print(f"ID: {post_id}")
    print(f"時間: {time}")
    print(f"內容: {text}")
    print(f"媒體類型: {media_type}")

def main():
    parser = argparse.ArgumentParser(description="列出和顯示 Threads 貼文")
    
    # 建立子命令
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 列出貼文的子命令
    list_parser = subparsers.add_parser("list", help="列出自己的貼文")
    list_parser.add_argument("-c", "--count", type=int, default=10, help="要顯示的貼文數量 (預設: 10)")
    list_parser.add_argument("-j", "--json", action="store_true", help="以 JSON 格式輸出")
    
    # 顯示特定貼文詳細資訊的子命令
    show_parser = subparsers.add_parser("show", help="顯示特定貼文的詳細資訊")
    show_parser.add_argument("post_id", help="要顯示的貼文 ID")
    show_parser.add_argument("-j", "--json", action="store_true", help="以 JSON 格式輸出")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_posts(args.count, args.json)
    elif args.command == "show":
        show_post_details(args.post_id, args.json)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 