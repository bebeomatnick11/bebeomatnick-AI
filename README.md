# Roblox AI Backend (FastAPI)

Backend nhận request từ Roblox → gửi câu hỏi tới AI → trả JSON về.

## Endpoint chính

### 1. Hỏi AI (mỗi player có brain riêng)

```
POST /api/v1/ai/ask
```

**Request:**
```json
{
  "question": "Hôm nay bạn thế nào?",
  "player_id": "123456789",
  "player_name": "NoobMaster69"
}
```

**Response:**
```json
{
  "success": true,
  "question": "Hôm nay bạn thế nào?",
  "answer": "...",
  "model": "gpt-4o-mini",
  "player_id": "123456789",
  "player_name": "NoobMaster69",
  "is_new_brain": false
}
```

### 2. Tạo brain mới (xóa ký ức cũ)

```
POST /api/v1/ai/reset
```

```json
{
  "player_id": "123456789"
}
```

---

## Deploy lên Render (khuyên dùng)

### Cách 1: Deploy bằng GitHub (khuyên dùng)

1. Tạo repository mới trên GitHub
2. Upload toàn bộ thư mục `api_backend` lên repo
3. Vào [https://dashboard.render.com](https://dashboard.render.com) → **New** → **Web Service**
4. Kết nối GitHub repo vừa tạo
5. Render sẽ tự nhận `render.yaml`. Hoặc điền thủ công:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Thêm Environment Variable quan trọng:
   - `OPENAI_API_KEY` = API key OpenAI của bạn
   - `OPENAI_MODEL` = gpt-4o-mini (hoặc model khác)
7. Bấm **Create Web Service**

Sau khi deploy xong, bạn sẽ có URL dạng:
```
https://roblox-ai-backend-xxxx.onrender.com
```

Endpoint dùng trong Roblox:
```
https://roblox-ai-backend-xxxx.onrender.com/api/v1/ai/ask
```

### Cách 2: Dùng Dockerfile

Render cũng hỗ trợ Dockerfile sẵn có trong project.

---

## Biến môi trường cần set trên Render

| Key                   | Bắt buộc | Mô tả                              |
|-----------------------|----------|------------------------------------|
| `OPENAI_API_KEY`      | Có       | API key OpenAI                     |
| `OPENAI_BASE_URL`     | Không    | Mặc định `https://api.openai.com/v1` |
| `OPENAI_MODEL`        | Không    | Mặc định `gpt-4o-mini`             |
| `OPENAI_SYSTEM_PROMPT`| Không    | System prompt                      |
| `DEBUG`               | Không    | Nên để `False` trên production     |

---

## Gọi từ Roblox (Luau)

```lua
local HttpService = game:GetService("HttpService")

local BACKEND_URL = "https://your-app.onrender.com/api/v1/ai/ask"  -- Đổi thành URL thật

local function askAI(question, playerName)
    local body = HttpService:JSONEncode({
        question = question,
        player_name = playerName
    })

    local success, response = pcall(function()
        return HttpService:RequestAsync({
            Url = BACKEND_URL,
            Method = "POST",
            Headers = { ["Content-Type"] = "application/json" },
            Body = body
        })
    end)

    if success and response.Success then
        local data = HttpService:JSONDecode(response.Body)
        return data.answer
    else
        warn("Lỗi gọi AI:", response)
        return "Xin lỗi, AI đang bận một chút."
    end
end
```

---

## Lưu ý quan trọng khi dùng Render Free

- Free tier sẽ **sleep** sau ~15 phút không có request.
- Request đầu tiên sau khi sleep có thể mất 30–60 giây (cold start).
- Nếu muốn luôn online, nâng lên paid plan hoặc dùng Railway / Fly.io.
