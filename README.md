# Threads 文言文自動回覆機器人

這是一個部署於 Vercel 的 Threads bot，用來自動回覆留言為文言文。

## 🌐 功能

- 接收 Threads 留言 webhook
- 呼叫 OpenAI GPT-4 轉換成文言文
- 使用 Threads API 自動回覆原留言
- 列出和查看自己的 Threads 貼文與內容
- 自動回覆貼文下尚未被回覆的留言
- 支援日期限制，只回覆特定日期範圍內的留言
- 支援限制回覆數量，可設定每篇貼文最多回覆幾條留言

## 🚀 快速部署

1. 申請 Threads API 與 OpenAI API 金鑰
2. 設定 Vercel 專案，並加上以下環境變數：

```
OPENAI_API_KEY=你的OpenAI金鑰
THREADS_ACCESS_TOKEN=你的Threads API Token
VERIFY_TOKEN=你自定的 webhook token
```

3. 將專案上傳至 Vercel，自動部署完成！

## 📋 環境需求

專案使用以下主要套件：
- Python 3.9+
- openai==1.75.0
- fastapi
- uvicorn
- requests
- python-dotenv
- argparse
- python-multipart

可透過以下指令安裝所需套件：
```bash
pip install -r requirements.txt
```

## 📂 專案結構

專案目錄結構如下：

```
threads_classical_bot/
├── api/                        # API 端點相關功能
│   ├── webhook.py              # 處理 Threads webhook 請求
│   └── list_posts.py           # Threads 貼文列表 API
│
├── utils/                      # 工具函數庫
│   ├── openai_client.py        # OpenAI API 文言文生成功能
│   ├── threads_api.py          # Threads API 操作功能
│   └── list_threads_posts.py   # 獲取 Threads 貼文功能
│
├── .env                        # 環境變數設定檔 (本地開發用)
├── .gitignore                  # Git 忽略檔案清單
├── README.md                   # 專案說明文件
├── requirements.txt            # 專案依賴套件清單
├── vercel.json                 # Vercel 部署設定
│
├── auto_reply_threads.py       # 自動回覆貼文下的留言工具
├── list_my_posts.py            # 命令列工具，列出和顯示貼文
├── run_server.py               # 啟動本地 API 伺服器
│
└── 測試工具/
    ├── test_openai_directly.py # 測試 OpenAI 文言文生成功能
    ├── test_openai.sh          # 使用 curl 測試 OpenAI API
    └── curl_test.sh            # 測試 webhook 的 curl 指令
```

### 檔案說明

#### 核心功能檔案

- **api/webhook.py** - 主要的 webhook 處理器，接收 Threads 的 webhook 通知並進行處理
- **api/list_posts.py** - 提供列出貼文的 API 端點
- **utils/openai_client.py** - 封裝 OpenAI GPT 文言文生成功能
- **utils/threads_api.py** - 封裝 Threads API 的存取與操作功能
- **utils/list_threads_posts.py** - 處理 Threads 貼文獲取功能
- **auto_reply_threads.py** - 主要的自動回覆腳本，用於回覆貼文下的留言
- **list_my_posts.py** - 命令列工具，用於列出和顯示自己的貼文
- **run_server.py** - 啟動本地 FastAPI 伺服器

#### 設定檔案

- **.env** - 本地開發用的環境變數設定檔
- **requirements.txt** - 專案所需的 Python 套件清單
- **vercel.json** - Vercel 部署設定，設定 API 路由與函式入口點
- **.gitignore** - Git 版本控制忽略檔案清單

#### 測試工具

- **test_openai_directly.py** - 直接測試 OpenAI API 的文言文生成功能
- **test_openai.sh** - Shell 腳本，使用 curl 測試 OpenAI API
- **curl_test.sh** - Shell 腳本，測試向 webhook 發送請求

## 🧩 使用方法

### 本地啟動伺服器

你可以在本地啟動伺服器來測試：

```bash
python run_server.py
```

啟動後，伺服器將在 http://0.0.0.0:8000 運行。

### 命令列方式查看貼文

你可以使用命令列工具查看自己的 Threads 貼文：

```bash
# 列出最近 10 篇貼文
python list_my_posts.py list

# 列出最近 20 篇貼文
python list_my_posts.py list -c 20

# 以 JSON 格式輸出
python list_my_posts.py list -j

# 顯示特定貼文的詳細資訊
python list_my_posts.py show 貼文ID
```

### API 方式查看貼文

啟動伺服器後，可以使用以下 API 端點：

- `GET /api/threads-posts?limit=10`：列出自己的貼文
- `GET /api/threads-post/{post_id}`：查看特定貼文的詳細資訊

### 自動回覆貼文下的留言

使用以下命令來自動回覆貼文下的留言：

```bash
# 處理特定貼文下的留言
python auto_reply_threads.py post 貼文ID

# 只回覆特定貼文下的前 5 條留言
python auto_reply_threads.py post 貼文ID -n 5

# 模擬處理特定貼文（不實際發送回覆）
python auto_reply_threads.py post 貼文ID -d

# 只回覆最近 3 天內的留言
python auto_reply_threads.py post 貼文ID --days 3

# 只回覆最近 7 天內的前 10 條留言
python auto_reply_threads.py post 貼文ID -n 10 --days 7

# 模擬處理特定貼文下的前 3 條留言
python auto_reply_threads.py post 貼文ID -n 3 -d

# 顯示詳細檢測資訊（預設開啟）
python auto_reply_threads.py post 貼文ID -v

# 不顯示詳細檢測資訊
python auto_reply_threads.py post 貼文ID -q

# 處理最近 5 篇貼文下的留言
python auto_reply_threads.py posts

# 處理最近 10 篇貼文，且每篇貼文只回覆前 2 條留言
python auto_reply_threads.py posts -c 10 -n 2

# 處理最近 10 篇貼文，只回覆 5 天內的留言
python auto_reply_threads.py posts -c 10 --days 5

# 模擬處理最近 5 篇貼文下的前 10 條留言
python auto_reply_threads.py posts -n 10 -d
```

#### 日期限制功能

使用 `--days` 參數可以限制只回覆特定天數內的留言：

```bash
# 只回覆 3 天內的留言
python auto_reply_threads.py post 貼文ID --days 3

# 回覆 7 天內的留言，每篇貼文最多處理 5 條
python auto_reply_threads.py posts --days 7 -n 5
```

這樣可以避免回覆太舊的留言，讓互動更具時效性。

#### 檢測已回覆用戶

當使用詳細模式 (`-v`) 時，工具會顯示以下資訊：

1. 貼文下你的所有回覆
2. 被視為已回覆的用戶列表
3. 需要回覆的留言內容

這樣你可以清楚地了解系統是如何判斷哪些用戶已被回覆過的。如果你不需要這些詳細資訊，可以使用 `-q` 參數關閉它。

#### 回覆邏輯說明

目前的檢測邏輯是：如果貼文下有你發布的回覆，則假設所有其他用戶都已被你回覆過。這是由於 Threads API 的限制，無法直接獲取一個回覆是針對哪條留言的。

這個工具會：
1. 檢查貼文下的所有留言
2. 識別哪些留言是尚未被你回覆的
3. 根據設定的回覆則數上限和日期範圍過濾留言
4. 使用 OpenAI 生成文言文回覆
5. 自動發送回覆給留言者

## 📝 開發與測試

專案提供了幾個測試腳本：

- `test_openai_directly.py`: 測試 OpenAI 文言文生成功能
- `test_openai.sh`: 使用 curl 測試 OpenAI API
- `curl_test.sh`: 測試 webhook 的 curl 指令

## 📚 維護說明

1. 更新 OpenAI 版本時，請確保在 `requirements.txt` 中更新對應版本
2. Vercel 部署時會自動安裝依賴並啟用 webhook
3. 本地測試時，請確保 `.env` 檔案中包含所有必要的環境變數

## 🔗 相關連結

- [Threads API 文件](https://developers.facebook.com/docs/instagram-api/guides/messaging)
- [OpenAI API 文件](https://platform.openai.com/docs/api-reference)
- [Vercel 部署指南](https://vercel.com/docs/projects/overview)