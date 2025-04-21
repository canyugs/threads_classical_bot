#!/bin/bash
# Threads API 測試腳本

# 設定 API 基本網址（根據您的伺服器設定調整）
API_URL="http://localhost:8000"

# 獲取當前用戶的 ID（僅作參考）
echo "==== 獲取當前 Threads 用戶 ID ===="
THREADS_USER_ID=$(curl -s "${API_URL}/api/threads-user-id")
echo "用戶 ID: ${THREADS_USER_ID}"

# 測試 OpenAI 古風回覆生成功能
echo -e "\n==== 測試 OpenAI 古風回覆生成功能 ===="
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，今天天氣真好！"}' \
  "${API_URL}/api/test-openai" | jq .

# 測試 GET /api/threads-user-info (threads_basic)
echo -e "\n==== 測試獲取 Threads 帳號資訊 ===="
curl -s "${API_URL}/api/threads-user-info" | jq .

# 測試 GET /api/threads-post-limit (threads_content_publish)
echo -e "\n==== 測試獲取發文限制 ===="
curl -s "${API_URL}/api/threads-post-limit" | jq .

# 測試 GET /api/threads-mentions (threads_manage_mentions)
echo -e "\n==== 測試獲取提及資訊 ===="
curl -s "${API_URL}/api/threads-mentions" | jq .

# 測試 GET /api/threads-replies (threads_read_replies)
echo -e "\n==== 測試獲取回覆資訊 ===="
curl -s "${API_URL}/api/threads-replies" | jq .

# 測試符合官方文檔的兩步驟發文流程
echo -e "\n==== 步驟 1：建立 Threads 媒體容器 ===="
CONTAINER_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "media_type": "TEXT",
    "text": "這是一則透過兩步驟 API 發佈的測試貼文 #測試",
    "link_attachment": "https://developers.facebook.com/"
  }' \
  "${API_URL}/api/threads")

echo $CONTAINER_RESPONSE | jq .

# 從回應中取得容器 ID
CONTAINER_ID=$(echo $CONTAINER_RESPONSE | jq -r '.id')
echo "取得的媒體容器 ID: $CONTAINER_ID"

# 檢查是否成功獲取容器 ID
if [ "$CONTAINER_ID" == "null" ] || [ -z "$CONTAINER_ID" ] || [ "$CONTAINER_ID" == "" ]; then
  echo "無法獲取媒體容器 ID，跳過發布步驟"
else
  # 等待 30 秒讓伺服器處理上傳（根據官方文檔建議）
  echo -e "\n正在等待 5 秒讓伺服器處理上傳..."
  sleep 5

  # 步驟 2：發布媒體容器
  echo -e "\n==== 步驟 2：發布 Threads 媒體容器 ===="
  POST_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{\"creation_id\": \"$CONTAINER_ID\"}" \
    "${API_URL}/api/threads-publish")
  
  echo $POST_RESPONSE | jq .
  
  # 從回應中取得貼文 ID 用於後續回覆測試
  POST_ID=$(echo $POST_RESPONSE | jq -r '.id')
  echo "取得的貼文 ID: $POST_ID"
  
  # 如果成功發布貼文，則測試回覆功能
  if [ "$POST_ID" != "null" ] && [ -n "$POST_ID" ] && [ "$POST_ID" != "" ]; then
    # 測試標準兩步驟回覆流程 - 步驟 1：建立回覆容器
    echo -e "\n==== 步驟 1：建立 Threads 回覆容器 ===="
    REPLY_CONTAINER_RESPONSE=$(curl -s -X POST \
      -H "Content-Type: application/json" \
      -d "{
        \"media_type\": \"TEXT\",
        \"text\": \"這是一則使用兩步驟 API 的測試回覆 #回覆測試\",
        \"reply_to_id\": \"$POST_ID\"
      }" \
      "${API_URL}/api/threads")
    
    echo $REPLY_CONTAINER_RESPONSE | jq .
    
    # 從回應中取得回覆容器 ID
    REPLY_CONTAINER_ID=$(echo $REPLY_CONTAINER_RESPONSE | jq -r '.id')
    echo "取得的回覆容器 ID: $REPLY_CONTAINER_ID"
    
    # 檢查是否成功獲取回覆容器 ID
    if [ "$REPLY_CONTAINER_ID" == "null" ] || [ -z "$REPLY_CONTAINER_ID" ] || [ "$REPLY_CONTAINER_ID" == "" ]; then
      echo "無法獲取回覆容器 ID，跳過發布步驟"
    else
      # 等待伺服器處理上傳
      echo -e "\n正在等待 5 秒讓伺服器處理上傳..."
      sleep 5
      
      # 步驟 2：發布回覆容器
      echo -e "\n==== 步驟 2：發布 Threads 回覆容器 ===="
      curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"creation_id\": \"$REPLY_CONTAINER_ID\"}" \
        "${API_URL}/api/threads-publish" | jq .
    fi
  else
    echo "無法獲取貼文 ID，跳過回覆測試"
  fi
fi

# 測試 Webhook (模擬 Threads 發送的回覆事件)
echo -e "\n==== 測試 Webhook 回調（包含 OpenAI 古風回覆生成） ===="
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "field": "threads",
        "value": {
          "replies": {
            "thread_id": "123456789",
            "text": "你好，請問你今天過得如何？",
            "from": {
              "id": "987654321"
            },
            "root_post": {
              "owner_id": "您的帳號ID"
            }
          }
        }
      }]
    }]
  }' \
  "${API_URL}/api/webhook" | jq .

# 測試模擬發送回覆
echo -e "\n==== 測試生成古風回覆並發送（完整流程）===="
TEST_REPLY_MESSAGE="今天天氣真不錯，你覺得呢？"
echo "原始訊息: $TEST_REPLY_MESSAGE"

# 使用 OpenAI 生成古風回覆
echo -e "\n生成古風回覆中..."
CLASSICAL_REPLY=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$TEST_REPLY_MESSAGE\"}" \
  "${API_URL}/api/test-openai" | jq -r '.reply')

echo "生成的古風回覆: $CLASSICAL_REPLY"

# 如果有有效的貼文ID（前面測試產生的），則嘗試回覆
if [ "$POST_ID" != "null" ] && [ -n "$POST_ID" ] && [ "$POST_ID" != "" ]; then
  echo -e "\n使用生成的古風文字進行回覆："
  
  # 使用一站式回覆接口
  curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "{
      \"reply_to_id\": \"$POST_ID\",
      \"text\": \"$CLASSICAL_REPLY\",
      \"media_type\": \"TEXT\"
    }" \
    "${API_URL}/api/create-reply" | jq .
else
  echo "沒有可用的貼文 ID，無法進行完整回覆測試"
fi 