# 🌐 RAG Bot Web UI - Quick Reference

##  Getting Started in 3 Steps

### Step 1: Install Dependencies

**Windows:**
```batch
setup.bat
```

**macOS/Linux:**
```bash
bash setup.sh
```

**Manual:**
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
```

### Step 3: Run the App

```bash
streamlit run app.py
```

The app opens automatically at: **http://localhost:8501**

---

## 📖 Using the Web UI

### 💬 Chat Tab

1. **Ask Questions**: Type naturally about your documents
2. **View Responses**: Get instant AI-powered answers
3. **Check Sources**: Click expand to see source documents
4. **Clear History**: Reset conversation with one click
5. **Export Chat**: Download as JSON for analysis

### 📊 Analytics Tab

- **Questions Asked**: Total count
- **Avg Response Time**: Performance metric
- **Error Count**: Track issues
- **Success Rate**: Quality indicator

### ⚙️ Settings Tab

- **Model Config**: Adjust temperature and retriever K
- **Document Config**: Change chunk size and overlap
- **View Rules**: See validation constraints
- **Bot Control**: Restart or reset statistics

### 📚 Help Tab

- **Getting Started**: Step-by-step tutorial
- **Tips & Tricks**: Best practices
- **Features**: Complete feature overview
- **About RAG**: Learn about the technology

---

## 🛠️ Configuration Options

### Model Settings

| Setting | Default | Range | Purpose |
|---------|---------|-------|---------|
| Temperature | 0.7 | 0.0-1.0 | Control creativity (lower = focused) |
| Retriever K | 4 | 1-10 | Number of documents to retrieve |
| Model | gpt-4o | - | LLM to use for answers |

### Document Settings

| Setting | Default | Purpose |
|---------|---------|---------|
| Chunk Size | 500 | Characters per document chunk |
| Chunk Overlap | 50 | Overlap between chunks |
| PDF Chunk Size | 500 | PDF processing chunk size |

### Validation Rules

| Rule | Min | Max | Purpose |
|------|-----|-----|---------|
| Question Length | 3 | 500 | Valid question range |
| Answer Length | 50 | 2000 | Valid answer range |

---

## 📱 Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│  🤖 RAG Bot - AI Document Assistant                     │
└─────────────────────────────────────────────────────────┘
│         │                                               │
│ Sidebar │            Main Content Area                  │
│         │                                               │
│ 📊 Bot  │  ┌─ 💬 Chat ─┬─ 📊 Analytics ┐              │
│ Status  │  │            │               │              │
│         │  │ ┌────────┐ │  Statistics   │              │
│ ⚙️ Model│  │ │History │ │  - Questions │              │
│ Config  │  │ │Area    │ │  - Time      │              │
│         │  │ └────────┘ │  - Errors    │              │
│ 📄 Docs │  │            │               │              │
│ Settings│  │ ┌────────┐ │  Metrics     │              │
│         │  │ │Question │ │  - Success % │              │
│ ℹ️ About│  │ │Input   │ │               │              │
│         │  │ └────────┘ │               │              │
│         │  │            │               │              │
│         │  └────────────┴───────────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow Example

### Step-by-Step Usage

1. **Initialize** ✓
   - Click "Initialize Bot" in sidebar
   - Wait 2-5 seconds for setup

2. **Ask Question** ✓
   - Type your question in the chat box
   - Click "Ask" button

3. **Get Answer** ✓
   - Bot retrieves relevant documents
   - Generates AI answer (2-4 seconds)
   - Shows sources

4. **Explore** ✓
   - Read the answer
   - Click "Source Documents" to see context
   - Review accuracy

5. **Track** ✓
   - Switch to Analytics tab
   - Monitor performance metrics
   - Check success rate

6. **Export** ✓
   - Click "Export Chat"
   - Download JSON file
   - Use for analysis

---

## ⚡ Performance Tips

### Speed Up Responses

1. **Reduce Chunk Size**
   - Settings → Chunk Size: 300 (vs default 500)
   - Faster processing, less context

2. **Lower Retriever K**
   - Settings → K: 2 (vs default 4)
   - Fewer documents = faster retrieval

3. **Adjust Temperature**
   - Settings → Temperature: 0.5 (vs default 0.7)
   - Lower = faster, more focused answers

### Improve Answer Quality

1. **Increase K**
   - Settings → K: 6-8
   - More context for better answers

2. **Increase Chunk Size**
   - Settings → Size: 800-1000
   - More document context

3. **Adjust Temperature**
   - Settings → Temperature: 0.8-0.9
   - Higher = more creative/detailed

---

## 🐛 Troubleshooting

### Issue: "Port 8501 is already in use"

**Solution:**
```bash
streamlit run app.py --server.port 8502
```

### Issue: "OPENAI_API_KEY not set"

**Solution:**
```bash
# Option 1: Add to .env file
echo OPENAI_API_KEY=sk-your-key > .env

# Option 2: Set environment variable
export OPENAI_API_KEY=sk-your-key
streamlit run app.py

# Option 3: Windows
set OPENAI_API_KEY=sk-your-key
streamlit run app.py
```

### Issue: "Bot Not Ready" status

**Solution:**
1. Check .env file has valid API key
2. Check internet connection
3. Click "Initialize Bot" button
4. Check OpenAI API status

### Issue: Slow responses

**Solutions:**
1. Check internet connection
2. Reduce retriever K (2-3)
3. Reduce chunk size (300-400)
4. Check OpenAI API quota

### Issue: "Something went wrong" error

**Solutions:**
1. Check bot is initialized
2. Try shorter question
3. Clear browser cache
4. Restart browser

---

##  Deployment

### Quick Cloud Deploy

**Streamlit Cloud (Free):**
1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect GitHub
4. Deploy!

**Docker:**
```bash
docker build -t rag-bot .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-xxx rag-bot
```

**Docker Compose:**
```bash
docker-compose up
```

---

## 📊 Features Checklist

-  Chat interface with history
-  Real-time answer generation
-  Source document tracking
-  Analytics dashboard
-  Configuration panel
-  Error handling
-  Input validation
-  Export functionality
-  Professional styling
-  Mobile responsive

---

## 🔐 Security Tips

1. **Never share API key**
   - Use .env file (never commit)
   - Use environment variables

2. **Validate all inputs**
   - Questions are auto-validated
   - Length and format checked

3. **Secure deployment**
   - Use HTTPS in production
   - Enable XSRF protection
   - Limit file uploads

4. **Monitor errors**
   - Check logs regularly
   - Track failed requests
   - Review analytics

---

## 📞 Support

- **Documentation**: Read README.md
- **Issues**: Check START_HERE.md
- **API Docs**: openai.com/docs
- **LangChain**: python.langchain.com

---

## 📝 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Enter | Submit question |
| Ctrl+A | Select all text |
| Ctrl+C | Copy text |
| F5 | Refresh page |
| Ctrl+Shift+Delete | Clear browser cache |

---

## 🎨 Customization

### Change Colors

Edit `app.py` CSS section:
```python
--primary: #0066cc          # Main blue
--secondary: #f0f4f8        # Light gray
--success: #10b981          # Green
--warning: #f59e0b          # Orange
--danger: #ef4444           # Red
```

### Add Custom Features

Modify `app.py` to add:
- New tabs
- Custom components
- Advanced analytics
- File upload support

---

**Happy using! **
