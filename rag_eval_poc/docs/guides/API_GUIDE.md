# 🔌 RAG Bot API - Simple Guide

## What is the API?

The API is a way for other programs to talk to the RAG Bot without using the web interface.

Think of it like a phone line: the web UI is like talking in person, the API is like calling on the phone.

---

## Quick Start

### 1. Start the API
```bash
python api.py
```

The API runs at: http://localhost:8000

### 2. Test It
Open in browser: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "bot_initialized": false
}
```

Done! API is working 

---

## Main API Endpoints

### 1. Health Check
**What:** Check if API is running

**Command:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "bot_initialized": true/false
}
```

---

### 2. Initialize Bot
**What:** Start the RAG Bot

**Command:**
```bash
curl -X POST http://localhost:8000/api/init
```

**Response:**
```json
{
  "initialized": true,
  "ready": true,
  "status": " Bot ready"
}
```

---

### 3. Ask a Question
**What:** Get an answer from the bot

**Command:**
```bash
curl -X POST http://localhost:8000/api/question \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

**Response:**
```json
{
  "answer": "RAG stands for Retrieval-Augmented Generation...",
  "sources": [
    {
      "content": "First 200 chars of document...",
      "source": "sample_doc.pdf"
    }
  ],
  "response_time": 2.5,
  "success": true
}
```

---

### 4. Get Status
**What:** Check if bot is ready

**Command:**
```bash
curl http://localhost:8000/api/status
```

**Response:**
```json
{
  "initialized": true,
  "ready": true,
  "status": " Bot ready"
}
```

---

### 5. Get Config
**What:** See current settings

**Command:**
```bash
curl http://localhost:8000/api/config
```

**Response:**
```json
{
  "model": "gpt-4o",
  "temperature": 0.7,
  "chunk_size": 500,
  "retriever_k": 4,
  "max_question_length": 500
}
```

---

## Python Example

### Simple Usage
```python
import requests

# Initialize bot
response = requests.post('http://localhost:8000/api/init')
print(response.json())

# Ask question
response = requests.post('http://localhost:8000/api/question',
    json={'question': 'What is load forecasting?'}
)
print(response.json())
```

### Full Example
```python
import requests
import json

BASE_URL = 'http://localhost:8000'

# 1. Initialize
print("Initializing bot...")
init = requests.post(f'{BASE_URL}/api/init')
print(init.json())

# 2. Ask questions
questions = [
    'What is electricity?',
    'How does forecasting work?',
    'What are applications?'
]

for q in questions:
    print(f"\nAsking: {q}")
    response = requests.post(f'{BASE_URL}/api/question',
        json={'question': q}
    )
    data = response.json()
    
    print(f"Answer: {data['answer'][:100]}...")
    print(f"Time: {data['response_time']:.2f}s")
    print(f"Sources: {len(data['sources'])}")
```

---

## JavaScript/Node Example

### Simple Usage
```javascript
// Initialize bot
const init = await fetch('http://localhost:8000/api/init', {
  method: 'POST'
});
console.log(await init.json());

// Ask question
const response = await fetch('http://localhost:8000/api/question', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'What is RAG?' })
});
console.log(await response.json());
```

---

## Error Handling

### What Errors Look Like
```json
{
  "detail": "Bot not initialized. Call /api/init first"
}
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Bot not initialized" | Haven't called /api/init | Call /api/init first |
| "Invalid question" | Question too short/long | Keep 3-500 characters |
| "Failed to generate answer" | API error | Check internet, retry |
| "Port 8000 already in use" | Port busy | Use different port |

---

## Running Multiple Instances

### Start on Different Ports
```bash
# Terminal 1
python api.py

# Terminal 2 - Different port
uvicorn api:app --port 8001

# Terminal 3 - Different port
uvicorn api:app --port 8002
```

Then use:
- http://localhost:8000 (API 1)
- http://localhost:8001 (API 2)
- http://localhost:8002 (API 3)

---

## Response Times

Typical times you should expect:

| Operation | Time |
|-----------|------|
| Initialize bot | 3-5 seconds |
| Ask question | 2-4 seconds |
| Get config | <1 second |
| Get status | <1 second |

---

## Troubleshooting

### API Won't Start
```bash
# Check if port is busy
# Try different port:
uvicorn api:app --port 8001
```

### API Won't Connect
```bash
# Check if it's running:
curl http://localhost:8000/health

# If not working, restart:
# 1. Stop current process (Ctrl+C)
# 2. Run again: python api.py
```

### Timeout Errors
```
# API takes too long to respond
# Solutions:
# 1. Check internet connection
# 2. Check OpenAI API status
# 3. Reduce K value in config.py
# 4. Try simpler questions
```

---

## Using with Web UI

You can run both at the same time:

```bash
# Terminal 1 - Web UI
streamlit run app.py

# Terminal 2 - API
python api.py
```

Then:
- Web UI: http://localhost:8501
- API: http://localhost:8000

---

## API Documentation (Auto-generated)

Swagger UI (interactive docs):
http://localhost:8000/docs

ReDoc (alternative docs):
http://localhost:8000/redoc

---

## Next Steps

### To Learn More
- See [SIMPLE_GUIDE.md](SIMPLE_GUIDE.md) for feature guide
- See [README.md](README.md) for technical details

### To Integrate
- Use API in your own apps
- Build custom interfaces
- Automate questions

### To Deploy
- See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud options

---

**API is ready to use! **
