#  RAG Bot Web UI - Step by Step Instructions

## Video of What You Built

Your RAG Bot now has a **professional, modern web interface** that anyone can use without terminal knowledge!

---

## Step 1: Install Everything (5 minutes)

### For Windows Users 🪟

```batch
# Open Command Prompt or PowerShell in your project folder
# Run the setup script:

setup.bat
```

**What it does:**
- Creates a Python virtual environment
- Installs all dependencies (Streamlit, LangChain, etc.)
- Creates necessary folders

### For Mac/Linux Users 🍎🐧

```bash
# Open Terminal in your project folder
# Run the setup script:

bash setup.sh
```

### Manual Installation (All Platforms)

```bash
# 1. Install Python packages
pip install -r requirements.txt

# 2. Create directories if needed
mkdir data/documents
mkdir chroma_db
mkdir .streamlit
```

---

## Step 2: Set Up Your API Key (2 minutes)

### Create `.env` File

In your project folder, create a new file named `.env`:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
```

**How to get your API key:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key
4. Paste it into `.env` file

 **IMPORTANT:** Never share this file! It's in `.gitignore` for a reason.

---

## Step 3: Run the Web UI (1 minute)

### Start Streamlit

```bash
streamlit run app.py
```

**What happens:**
- The app starts locally
- Your browser opens automatically (or navigate to http://localhost:8501)
- You see the professional RAG Bot interface

---

## Step 4: Use the Web UI (First Time)

### 1. Initialize the Bot
- Click the **"Initialize Bot"** button in the left sidebar
- Wait 3-5 seconds for setup
- Status changes to ** Bot Ready**

### 2. Ask Your First Question
- Go to the **💬 Chat** tab
- Type a question: "What is electricity load forecasting?"
- Click **🔍 Ask** or press Enter
- Wait 2-4 seconds for the answer

### 3. View Source Documents
- Under the answer, click **"📚 Source Document(s)"**
- See which documents were used
- Verify the answer is accurate

### 4. Explore the Interface
- **📊 Analytics** tab: See questions asked, response times
- **⚙️ Settings** tab: Adjust model parameters
- **📚 Help** tab: Learn tips and features
- **💾 Export**: Save chat as JSON

---

## Complete Feature Walkthrough

### 💬 Chat Tab
```
┌─────────────────────────────────────┐
│ Your Question Input                 │
│ [What is forecasting?............] 🔍│
└─────────────────────────────────────┘
          ↓ Click Ask ↓
┌─────────────────────────────────────┐
│ 👤 You: What is forecasting?        │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ 🤖 Bot: Forecasting is...          │
│ (detailed answer here)              │
└─────────────────────────────────────┘
│ 📚 Source Documents (3) ▼          │
│ ├─ Document 1 excerpt             │
│ ├─ Document 2 excerpt             │
│ └─ Document 3 excerpt             │
└─────────────────────────────────────┘
```

### 📊 Analytics Tab
```
┌──────────────┬──────────────┬──────────────┐
│ Questions    │ Avg Time     │ Errors       │
│ Asked: 5     │ 3.2 seconds  │ 0            │
└──────────────┴──────────────┴──────────────┘
```

### ⚙️ Settings Tab
- **Temperature**: 0.1 (focused) to 1.0 (creative)
- **Retriever K**: 1-10 documents to retrieve
- **Chunk Size**: Document chunk size
- **Chunk Overlap**: Context overlap between chunks

### 📚 Help Tab
- Getting Started guide
- Tips and tricks
- Complete feature list
- About RAG technology

---

## Common Tasks

### Task 1: Ask a Different Question
1. Click the Chat tab
2. Type your new question
3. Click Ask

### Task 2: Clear Conversation
1. Click the Chat tab
2. Click **🗑️ Clear History**
3. History is cleared

### Task 3: Download Chat
1. Click the Chat tab
2. Click **💾 Export Chat**
3. Click **📥 Download JSON**
4. File downloads (e.g., `rag_chat_20240115_143022.json`)

### Task 4: Adjust Model Settings
1. Click the Settings tab
2. Change parameters:
   - Temperature (affects creativity)
   - K (number of documents)
3. Changes apply immediately

### Task 5: Reset Everything
1. Click Settings tab
2. Click **🔄 Restart Bot** to reinitialize
3. Click **🗑️ Reset Stats** to clear statistics

---

## Troubleshooting

###  Issue: "Bot Not Ready" Status

**Solution:**
```bash
# Check your .env file has the API key
cat .env

# If empty, add:
echo OPENAI_API_KEY=sk-your-key > .env

# Restart the app:
# Press Ctrl+C to stop
# Run again: streamlit run app.py
```

###  Issue: Port Already in Use

**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

Then open: http://localhost:8502

###  Issue: API Key Not Found

**Solution:**
```bash
# Make sure .env file exists in project root
# And contains: OPENAI_API_KEY=sk-xxxxx

# Or set environment variable:
export OPENAI_API_KEY=sk-your-key
streamlit run app.py
```

###  Issue: Slow Responses

**Solutions:**
1. Check internet connection
2. In Settings, reduce K from 4 to 2
3. In Settings, reduce chunk size to 300
4. Check OpenAI API status

###  Issue: Blank Page

**Solutions:**
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Restart the app

---

## Performance Tips

### For Faster Responses
- Settings → Temperature: 0.5 (lower = faster)
- Settings → K: 2 (fewer documents)
- Settings → Chunk Size: 300 (smaller chunks)

### For Better Answers
- Settings → Temperature: 0.8 (higher = more creative)
- Settings → K: 6-8 (more context)
- Settings → Chunk Size: 800 (larger chunks)
- Ask specific, detailed questions

### For Accurate Answers
- Ask one question at a time
- Use 3-500 character questions
- Include context if needed
- Check source documents

---

## Deployment (When Ready)

### Easy Cloud Deployment

**Option 1: Streamlit Cloud (Recommended)**
1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Click "New app"
4. Connect your repo
5. Deploy!

**Option 2: Docker**
```bash
docker build -t rag-bot .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-xxx rag-bot
```

**Option 3: Docker Compose**
```bash
docker-compose up
```

See `DEPLOYMENT.md` for more options.

---

## File Structure (What Was Created)

```
rag_eval_poc/
├── app.py                          # Main web app (NEW!)
├── WEB_UI_GUIDE.md                 # Quick reference
├── DEPLOYMENT.md                   # Deployment options
├── TESTING_GUIDE.md                # Testing checklist
├── setup.bat / setup.sh            # Auto setup
├── .streamlit/config.toml          # Streamlit config
├── Dockerfile                      # Docker container
├── docker-compose.yml              # Docker Compose
├── .gitignore                      # Git rules
├── requirements.txt                # Dependencies (updated)
├── config.py                       # Configuration
├── validators.py                   # Validation
├── demo.py                         # Core logic
├── rag/
│   ├── loader.py
│   ├── vector_store.py
│   └── rag_chain.py
└── data/documents/                 # Your PDFs go here
```

---

## Key Files Overview

| File | Purpose |
|------|---------|
| **app.py** | Streamlit web interface |
| **config.py** | All settings (API key, models, etc.) |
| **demo.py** | RAG bot core logic |
| **rag/loader.py** | PDF document loading |
| **rag/vector_store.py** | Vector database |
| **rag/rag_chain.py** | Answer generation |
| **.env** | API keys ( don't share!) |

---

## Next Steps After Trying It

### 1. Add Your Own Documents
```bash
# Put PDF files in:
data/documents/

# They'll be used automatically when bot initializes
```

### 2. Customize Settings
Edit `config.py` to:
- Change default temperature
- Adjust chunk sizes
- Modify validation rules

### 3. Deploy Online
Follow `DEPLOYMENT.md` for:
- Streamlit Cloud (easiest)
- Docker deployment
- AWS/Azure deployment

### 4. Learn More
- Read `README.md` for detailed docs
- Check `ARCHITECTURE.md` for technical details
- See `WEB_UI_GUIDE.md` for UI reference

---

## FAQ

**Q: Where are my API keys stored?**
A: In `.env` file (never committed to git). Also never displayed in UI.

**Q: Can I use my own documents?**
A: Yes! Put PDFs in `data/documents/` and reinitialize.

**Q: How long do responses take?**
A: Typically 2-4 seconds. Depends on document size and API.

**Q: Can I export my conversations?**
A: Yes! Click "Export Chat" → "Download JSON" in the Chat tab.

**Q: Is it production-ready?**
A: Yes! See `DEPLOYMENT.md` for deployment options.

**Q: Can I customize the colors?**
A: Yes! Edit CSS in `app.py` under `configure_styling()` function.

**Q: How many questions can it handle?**
A: Unlimited! Statistics track everything.

**Q: Can I run this offline?**
A: Not without OpenAI API. You need internet for LLM.

---

## Quick Command Reference

```bash
# Install everything
pip install -r requirements.txt

# Run the web UI
streamlit run app.py

# Stop the app
# Press Ctrl+C

# Use different port
streamlit run app.py --server.port 8502

# Debug mode
streamlit run app.py --logger.level=debug

# Docker
docker build -t rag-bot .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-xxx rag-bot
```

---

## Support & Resources

- **Documentation**: [README.md](README.md)
- **Quick Start**: [START_HERE.md](START_HERE.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Testing**: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Web UI Guide**: [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)

---

## You're All Set! 🎉

**Now run:**
```bash
streamlit run app.py
```

**Then open:**
http://localhost:8501

**Enjoy your new AI-powered document assistant!** 
