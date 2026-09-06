🤖 Roblox AI Backend

Backend API cho Roblox AI Companion, xây dựng bằng FastAPI + OpenAI API.

Backend đóng vai trò trung gian giữa Roblox và OpenAI:

Roblox Game
    │
    │ HTTPS
    ▼
FastAPI Backend
    │
    ├── Player Memory
    ├── Conversation Context
    ├── Database
    │
    │ OpenAI API
    ▼
GPT-5.6 Luna
    │
    ▼
AI Response
    │
    ▼
Roblox AI Companion

Backend được thiết kế để:

- 🤖 Kết nối Roblox với OpenAI
- 🧠 Lưu memory riêng cho từng player
- 💬 Duy trì lịch sử hội thoại
- 🔐 Giữ OpenAI API key ở server
- ⚡ Hỗ trợ request từ Roblox qua HTTPS
- 🔄 Reset memory theo từng player
- 🗄️ Lưu dữ liệu bằng database
- 📱 Hoạt động với Roblox trên mobile và PC
- 🚀 Có thể deploy lên Render hoặc các nền tảng hỗ trợ FastAPI

---

✨ Features

🤖 OpenAI Integration

Backend sử dụng OpenAI API để xử lý câu hỏi từ Roblox.

Model mặc định:

gpt-5.6-luna

OpenAI mô tả GPT-5.6 Luna là model được tối ưu cho các workload cần chi phí thấp và số lượng request lớn, phù hợp với backend AI có nhiều lượt tương tác.

Model có thể thay đổi thông qua environment variable:

OPENAI_MODEL=gpt-5.6-luna

Không cần sửa source code khi muốn đổi model.

---

🧠 Player Memory

Mỗi player có memory riêng.

Ví dụ:

Player A
 ├── Hello
 ├── My name is Alex
 └── Remember that I like Roblox

Player B
 ├── Hello
 └── My name is Bob

AI của Player A không được sử dụng memory của Player B.

Memory được xác định bằng:

player_id

Ví dụ:

{
  "question": "Tên tôi là gì?",
  "player_id": "123456789",
  "player_name": "Alex"
}

Backend sử dụng "player_id" để xác định conversation/memory tương ứng.

---

📡 API

Health Check

GET /health

Response:

{
  "status": "ok"
}

Dùng endpoint này để kiểm tra backend có đang hoạt động hay không.

---

Ask AI

POST /api/v1/ai/ask

Request

{
  "question": "Xin chào! Bạn là ai?",
  "player_id": "123456789",
  "player_name": "Alex"
}

Response

{
  "ok": true,
  "answer": "Xin chào Alex! Tôi là AI Companion của bạn.",
  "model": "gpt-5.6-luna"
}

«Response thực tế có thể chứa thêm metadata tùy phiên bản backend.»

---

Reset Player Memory

POST /api/v1/ai/reset

Request:

{
  "player_id": "123456789"
}

Endpoint này chỉ reset memory của player được chỉ định.

Ví dụ:

Player A → reset
Player B → không bị ảnh hưởng

---

🎮 Roblox Example

Roblox có thể gọi backend bằng "HttpService".

Ví dụ:

local HttpService = game:GetService("HttpService")

local BACKEND_URL = "https://YOUR-BACKEND.onrender.com"

local function askAI(question, player)
    local payload = {
        question = question,
        player_id = tostring(player.UserId),
        player_name = player.Name
    }

    local success, response = pcall(function()
        return HttpService:RequestAsync({
            Url = BACKEND_URL .. "/api/v1/ai/ask",
            Method = "POST",

            Headers = {
                ["Content-Type"] = "application/json"
            },

            Body = HttpService:JSONEncode(payload)
        })
    end)

    if not success then
        warn("AI request failed:", response)
        return nil
    end

    if not response.Success then
        warn("Backend returned:", response.StatusCode)
        return nil
    end

    local data = HttpService:JSONDecode(response.Body)

    if data.ok then
        return data.answer
    end

    return nil
end

Ví dụ sử dụng:

local answer = askAI(
    "Bạn nghĩ gì về game này?",
    player
)

if answer then
    print("AI:", answer)
end

---

🔐 Security

API Key KHÔNG được đặt trong Roblox

Tuyệt đối không làm:

local OPENAI_API_KEY = "sk-xxxxxxxx"

hoặc:

OPENAI_API_KEY = "sk-xxxxxxxx"

API key phải được lưu ở Environment Variables của server.

Luồng đúng:

Roblox
   │
   │ question
   ▼
Backend
   │
   │ OPENAI_API_KEY
   ▼
OpenAI

API key:

❌ Roblox
❌ LocalScript
❌ README
❌ GitHub
❌ .env commit lên GitHub

✅ Backend Environment Variables

Nếu API key bị lộ, cần revoke/rotate key ngay lập tức.

---

⚙️ Environment Variables

Backend sử dụng các biến môi trường sau:

APP_NAME="Roblox AI Backend"
APP_VERSION="1.0.0"

DEBUG=False

DATABASE_URL="sqlite:///./app.db"

SECRET_KEY="change-this-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=30

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5.6-luna

OPENAI_SYSTEM_PROMPT="Bạn là một trợ lý AI thân thiện trong game Roblox. Trả lời ngắn gọn, rõ ràng và vui vẻ."

Required

OPENAI_API_KEY

Optional

OPENAI_MODEL
OPENAI_BASE_URL
OPENAI_SYSTEM_PROMPT
DATABASE_URL
SECRET_KEY
DEBUG

---

🧪 ".env.example"

Repository chỉ nên chứa:

APP_NAME="Roblox AI Backend"
APP_VERSION="1.0.0"
DEBUG=False

DATABASE_URL="sqlite:///./app.db"

SECRET_KEY="your-super-secret-key-change-this-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=30

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5.6-luna
OPENAI_SYSTEM_PROMPT="Bạn là một trợ lý AI thân thiện trong game Roblox. Trả lời ngắn gọn, rõ ràng và vui vẻ."

Không bao giờ commit API key thật.

---

📁 Project Structure

api_backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── ai.py
│   │       └── items.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── item.py
│   │   └── player.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── ai.py
│   │   └── item.py
│   │
│   └── services/
│       ├── __init__.py
│       └── ai_service.py
│
├── tests/
│   ├── __init__.py
│   └── test_items.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
├── README.md
├── render.yaml
├── requirements.txt
├── run.py
└── runtime.txt

---

🧩 Architecture

Backend được chia thành nhiều layer.

"app/main.py"

Entry point của FastAPI.

Nhiệm vụ chính:

Create FastAPI app
        ↓
Register routers
        ↓
Start API

Không chứa API key.

---

"app/core/config.py"

Quản lý configuration.

Ví dụ:

OPENAI_API_KEY
OPENAI_MODEL
OPENAI_BASE_URL
OPENAI_SYSTEM_PROMPT

API key được đọc từ environment variables.

---

"app/api/routes/ai.py"

Chứa các API endpoint liên quan đến AI:

POST /api/v1/ai/ask
POST /api/v1/ai/reset

---

"app/services/ai_service.py"

Chứa logic AI:

Request
   ↓
Load player memory
   ↓
Build conversation context
   ↓
Call OpenAI
   ↓
Save response
   ↓
Return result

---

"app/models/player.py"

Database model cho player và message/memory.

Mục tiêu:

Player
 └── Messages
      ├── User
      ├── Assistant
      ├── User
      └── Assistant

---

"app/db/database.py"

Quản lý:

- Database engine
- Session
- Database connection

---

🧠 Memory Isolation

Backend phải đảm bảo memory được tách biệt theo "player_id".

Ví dụ:

Player 111
    └── "Tôi thích anime"

Player 222
    └── "Tôi thích Minecraft"

Khi Player 111 hỏi:

"Tôi thích gì?"

AI chỉ được sử dụng memory của Player 111.

Không được lấy:

Player 222

để trả lời.

---

🔄 Reset Memory

Khi gọi:

POST /api/v1/ai/reset

với:

{
  "player_id": "111"
}

chỉ memory của:

Player 111

được reset.

Player khác vẫn giữ nguyên memory.

---

🛠️ Local Development

1. Clone repository

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

---

2. Tạo virtual environment

Linux/macOS:

python -m venv .venv
source .venv/bin/activate

Windows:

python -m venv .venv
.venv\Scripts\activate

---

3. Install dependencies

pip install -r requirements.txt

---

4. Tạo ".env"

Copy:

.env.example

thành:

.env

Sau đó điền API key:

OPENAI_API_KEY=YOUR_REAL_API_KEY

Không commit ".env".

".gitignore" đã được cấu hình để bỏ qua file này.

---

5. Start server

python run.py

Hoặc:

uvicorn app.main:app --reload

Server mặc định:

http://127.0.0.1:8000

---

📚 API Documentation

FastAPI tự động tạo Swagger UI.

Sau khi server chạy:

/docs

Ví dụ:

http://127.0.0.1:8000/docs

Ngoài ra có:

/redoc

Swagger có thể được sử dụng để test:

GET /health
POST /api/v1/ai/ask
POST /api/v1/ai/reset

---

☁️ Deploy lên Render

1. Push repository lên GitHub

Đảm bảo repository không chứa:

.env

hoặc API key thật.

---

2. Tạo Web Service

Trên Render:

New → Web Service

Chọn GitHub repository.

---

3. Build Command

pip install -r requirements.txt

---

4. Start Command

PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port $PORT

---

5. Environment Variables

Thêm:

OPENAI_API_KEY

Giá trị:

YOUR_REAL_OPENAI_API_KEY

Thêm:

OPENAI_MODEL

Giá trị:

gpt-5.6-luna

Có thể thêm:

OPENAI_BASE_URL=https://api.openai.com/v1

và:

DEBUG=False

---

🌐 Sau khi Deploy

Render sẽ cung cấp URL dạng:

https://your-backend.onrender.com

Kiểm tra:

https://your-backend.onrender.com/health

Nếu hoạt động:

{
  "status": "ok"
}

Roblox sử dụng:

local BACKEND_URL = "https://your-backend.onrender.com"

Sau đó request:

POST /api/v1/ai/ask

---

⚠️ Database

Development có thể sử dụng SQLite:

DATABASE_URL=sqlite:///./app.db

SQLite phù hợp để:

- development
- testing
- prototype
- single-instance experiments

Đối với production thực tế với nhiều player hoặc nhiều instance backend, nên cân nhắc database persistent như PostgreSQL.

Đặc biệt, không nên giả định rằng filesystem local của một hosting platform luôn là nơi lưu trữ database lâu dài.

---

🚦 Error Handling

Backend nên xử lý các trường hợp:

400 → Invalid request
401 → Authentication/API configuration error
404 → Endpoint not found
429 → Rate limit / temporary overload
500 → Internal server error

Client Roblox không nên crash khi backend lỗi.

Ví dụ:

local success, result = pcall(function()
    -- request
end)

if not success then
    warn("AI backend unavailable")
end

---

🛡️ Production Security Checklist

Trước khi public backend:

- [ ] Không có API key trong source code
- [ ] Không có API key trong GitHub
- [ ] ".env" nằm trong ".gitignore"
- [ ] "DEBUG=False"
- [ ] "SECRET_KEY" được thay đổi
- [ ] API có rate limiting
- [ ] Validate "player_id"
- [ ] Giới hạn độ dài "question"
- [ ] Không cho client tự gửi system prompt
- [ ] Không log API key
- [ ] Không log sensitive information
- [ ] Xử lý OpenAI errors
- [ ] Có timeout cho OpenAI request
- [ ] Có giới hạn request từ Roblox

---

💰 OpenAI Cost

Chi phí phụ thuộc vào model và lượng token sử dụng.

GPT-5.6 Luna hiện được OpenAI niêm yết ở mức:

Input:  $0.20 / 1M tokens
Output: $1.20 / 1M tokens

Đây là lý do Luna phù hợp với backend có nhiều lượt chat ngắn như AI Companion. Giá/model có thể thay đổi theo thời gian, vì vậy hãy kiểm tra pricing/model documentation trước khi triển khai production.

---

📈 Scaling

Khi project lớn hơn, có thể bổ sung:

Rate limiting
      ↓
Authentication
      ↓
PostgreSQL
      ↓
Redis
      ↓
Caching
      ↓
Multiple backend instances

Có thể mở rộng thành:

                 ┌── OpenAI
                 │
Roblox → API → AI Service
                 │
                 ├── PostgreSQL
                 │
                 ├── Redis
                 │
                 └── Player Memory

---

🧪 Testing

Chạy test:

pytest

Test nên bao gồm:

✓ Health endpoint
✓ AI request validation
✓ Missing player_id
✓ Empty question
✓ Player memory isolation
✓ Memory reset
✓ Database persistence
✓ OpenAI error handling

Đặc biệt cần kiểm tra:

Player A memory
        ≠
Player B memory

---

🚫 Không Commit Secrets

Các file sau không được commit:

.env
.env.local
*.db
*.sqlite3

Không được viết:

OPENAI_API_KEY = "sk-..."

trong source code.

Không được viết:

local API_KEY = "sk-..."

trong Roblox.

API key chỉ tồn tại ở backend environment.

---

📝 Example Request

curl -X POST "https://YOUR-BACKEND.onrender.com/api/v1/ai/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Xin chào!",
    "player_id": "123456789",
    "player_name": "Alex"
  }'

---

📤 Example Response

{
  "ok": true,
  "answer": "Xin chào Alex! 👋",
  "model": "gpt-5.6-luna"
}

---

🧹 Reset Example

curl -X POST "https://YOUR-BACKEND.onrender.com/api/v1/ai/reset" \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "123456789"
  }'

---

🎯 Project Goal

Mục tiêu cuối cùng của project là xây dựng một AI Companion thực sự trong Roblox:

                 ┌─────────────────────┐
                 │    Roblox Player    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   AI Companion      │
                 │                     │
                 │ • Chat              │
                 │ • Follow Player     │
                 │ • Personality       │
                 │ • Memory            │
                 │ • Perception        │
                 │ • Actions           │
                 └──────────┬──────────┘
                            │
                         HTTPS
                            │
                            ▼
                 ┌─────────────────────┐
                 │   FastAPI Backend   │
                 │                     │
                 │ • API               │
                 │ • Memory            │
                 │ • Database          │
                 │ • Security          │
                 └──────────┬──────────┘
                            │
                       OpenAI API
                            │
                            ▼
                 ┌─────────────────────┐
                 │   GPT-5.6 Luna      │
                 └─────────────────────┘

---

📜 License

Thêm license phù hợp với project nếu repository được public.

Nếu chưa quyết định license, không nên tự động tuyên bố một license cụ thể.

---

⚠️ Important

Đây là backend proxy cho Roblox.

Roblox không gọi OpenAI API trực tiếp.

Đúng:

Roblox
   ↓
Your Backend
   ↓
OpenAI

Không nên:

Roblox
   ↓
OpenAI API + API key

API key phải được giữ ở server.

---

🚀 Status

Project: Roblox AI Companion Backend
Framework: FastAPI
AI Provider: OpenAI
Default Model: GPT-5.6 Luna
Database: SQLAlchemy
Development DB: SQLite
Deployment: Render
Client: Roblox

Backend is designed to keep the AI provider and API credentials on the server while allowing Roblox to communicate with the AI through a controlled HTTPS API.
