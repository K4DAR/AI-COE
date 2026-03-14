# ⚡ Setup in 5 Minutes

## What You Need

- Python 3.9+ (get from python.org)
- OpenAI API key (get from openai.com)
- Internet connection
- 5 minutes of time

---

## Step 1: Install Python Packages (1 minute)

```bash
pip install -r requirements.txt
```

This installs everything: Streamlit, LangChain, FastAPI, etc.

---

## Step 2: Get Your API Key (1 minute)

1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (looks like: sk-...)
4. Keep it safe! Don't share!

---

## Step 3: Create .env File (1 minute)

In your project folder, create a file named `.env`:

```
OPENAI_API_KEY=sk-your-key-here
```

Replace `sk-your-key-here` with your actual key.

**That's it!** The `.env` file is in `.gitignore` so your key won't be shared.

---

## Step 4: Run the App (2 minutes)

### Option A: Web Interface (Recommended)
```bash
streamlit run app.py
```

Opens at: http://localhost:8501

### Option B: API Server
```bash
python api.py
```

Opens at: http://localhost:8000

### Option C: Both (Advanced)
```bash
# Terminal 1
streamlit run app.py

# Terminal 2
python api.py
```

---

## Done! 🎉

### You can now:
-  Ask questions about documents
-  View analytics
-  Change settings
-  Export conversations
-  Use the API

---

## Troubleshooting

### "OPENAI_API_KEY not found"
→ Check your `.env` file has the key

### "ModuleNotFoundError"
→ Run: `pip install -r requirements.txt`

### "Port 8501 already in use"
→ Run: `streamlit run app.py --server.port 8502`

### "Cannot connect to OpenAI"
→ Check internet, check API key is valid

---

## Next: Read the Guides

- **Feature Guide**: [SIMPLE_GUIDE.md](SIMPLE_GUIDE.md)
- **API Guide**: [API_GUIDE.md](API_GUIDE.md)
- **Full Docs**: [README.md](README.md)

---

**That's everything! Enjoy! **
