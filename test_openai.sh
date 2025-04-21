#!/bin/bash
# OpenAI 古風回覆測試腳本

# 設定 API 基本網址（根據您的伺服器設定調整）
API_URL="http://localhost:8000"

# 測試訊息列表
declare -a test_messages=(
    "你好，今天天氣真好！"
    "我最近心情不錯，想出去走走。"
    "這部電影好看嗎？我在考慮要不要去看。"
    "你喜歡喝咖啡嗎？我每天早上都要喝一杯。"
    "討論一下人工智能的發展趨勢吧。"
)

echo "==== OpenAI 古風回覆功能測試 ===="
echo "共測試 ${#test_messages[@]} 條訊息"
echo "------------------------------"

# 執行測試
for (( i=0; i<${#test_messages[@]}; i++ ))
do
    message="${test_messages[$i]}"
    echo -e "\n測試 #$((i+1))："
    echo "原始訊息：$message"
    
    response=$(curl -s -X POST \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"$message\"}" \
      "${API_URL}/api/test-openai")
    
    # 解析回應
    if echo "$response" | grep -q "error"; then
        echo "錯誤：$(echo $response | jq -r '.error // "未知錯誤"')"
        echo "詳情：$(echo $response | jq -r '.details // "無詳細資訊"')"
    else
        reply=$(echo $response | jq -r '.reply // "無回覆"')
        echo -e "古風回覆：\033[1;32m$reply\033[0m"
    fi
    
    echo "------------------------------"
done

# 互動式測試
echo -e "\n==== 互動式測試 ===="
echo "現在您可以輸入自己的訊息進行測試"
echo "輸入 'exit' 或 'quit' 結束測試"

while true; do
    echo -e "\n請輸入您想轉換為古風風格的訊息："
    read -r user_input
    
    # 檢查退出指令
    if [[ "$user_input" == "exit" || "$user_input" == "quit" ]]; then
        echo "測試結束"
        break
    fi
    
    # 發送請求
    response=$(curl -s -X POST \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"$user_input\"}" \
      "${API_URL}/api/test-openai")
    
    # 解析回應
    if echo "$response" | grep -q "error"; then
        echo "錯誤：$(echo $response | jq -r '.error // "未知錯誤"')"
    else
        reply=$(echo $response | jq -r '.reply // "無回覆"')
        echo -e "古風回覆：\033[1;32m$reply\033[0m"
    fi
done 