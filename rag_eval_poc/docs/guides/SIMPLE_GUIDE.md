# 📚 RAG Bot - Simple Feature Guide

## 🎯 What is RAG Bot?

RAG Bot is an AI assistant that:
1. **Reads** your PDF documents
2. **Understands** them using AI
3. **Answers** your questions based on what it learned

Think of it like asking a smart assistant who has memorized all your documents.

---

##  Quick Start (2 minutes)

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
Create a `.env` file:
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Run
```bash
streamlit run app.py
```

Open: http://localhost:8501

Done! 🎉

---

## 💬 Chat Feature

### How to Use
1. Click the **Chat** tab
2. Type your question
3. Press **Enter** or click **Ask**
4. Wait for the answer (2-4 seconds)

### Example Questions
- "What is electricity load forecasting?"
- "How does the system work?"
- "Summarize the main points"

### Tips
- Ask specific questions
- Keep questions between 3-500 characters
- One question at a time
- Check source documents for accuracy

### Source Documents
After you get an answer:
- Click **📚 Source Documents**
- See which parts of your PDFs were used
- Verify the answer is accurate

---

## 📊 Analytics Feature

### What It Shows
- **Questions Asked**: How many questions you've asked
- **Avg Response Time**: How fast the system responds
- **Errors**: How many errors occurred
- **Success Rate**: Percentage of successful answers

### Why It Matters
- Slow responses = Maybe API is busy
- High errors = Might need to restart
- Low success = Questions might be unclear

### How to Use
1. Click **Analytics** tab
2. See your statistics
3. Use this to optimize your questions

---

## ⚙️ Settings Feature

### Temperature (0.0 - 1.0)
**What it does:** Controls how "creative" the AI is

| Value | Style | Use Case |
|-------|-------|----------|
| 0.1 | Focused, specific | Facts and data |
| 0.5 | Balanced | General questions |
| 0.9 | Creative, detailed | Explanations |

**How to use:** Drag the slider left (focused) or right (creative)

### Retriever K (1-10)
**What it does:** How many documents to search

| Value | Speed | Quality |
|-------|-------|---------|
| 2 | Fast | Basic answers |
| 4 | Normal | Good answers |
| 8 | Slow | Detailed answers |

**How to use:** For more context, increase K. For speed, decrease K.

### Chunk Size
**What it does:** How big each document piece is

| Size | Speed | Quality |
|------|-------|---------|
| 300 | Fast | Fragmented |
| 500 | Normal | Balanced |
| 1000 | Slow | Detailed |

**How to use:** Larger chunks = more context, slower

---

## 💾 Export Feature

### What It Does
Saves your conversation as a file you can open later

### How to Export
1. Click **Chat** tab
2. Click **💾 Export Chat**
3. Click **📥 Download JSON**
4. File downloads to your computer

### File Format
Your conversations are saved as JSON:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "messages": [
    {
      "role": "user",
      "content": "Your question"
    },
    {
      "role": "assistant",
      "content": "Bot answer"
    }
  ],
  "stats": {
    "total_questions": 5,
    "total_time": 12.5,
    "errors": 0
  }
}
```

### What to Do With It
- Share with team members
- Keep for your records
- Import to other tools
- Archive for later review

---

## 🔄 Clear History Feature

### What It Does
Removes all past conversations

### When to Use
- Start a new topic
- Clean up the interface
- Reset statistics

### How to Use
1. Click **Chat** tab
2. Click **🗑️ Clear History**
3. All messages are deleted
4. Start fresh

**Warning:** This is permanent! Can't undo.

---

## 🆘 Troubleshooting

### "Bot Not Ready"
**Problem:** Status shows red 

**Solution:**
1. Check your .env file has API key
2. Click "Initialize Bot" button
3. Wait 3-5 seconds

### "Answer is Wrong"
**Problem:** Bot gives incorrect information

**Solutions:**
- Check source documents (expand them)
- Ask a more specific question
- Try higher Temperature (0.8) for details
- Try higher K (6-8) for more context

### "Slow Responses"
**Problem:** Takes more than 5 seconds

**Solutions:**
1. Check internet connection
2. Reduce K to 2-3
3. Reduce Temperature to 0.5
4. Try shorter questions

### "Empty Answer"
**Problem:** Bot returns nothing

**Solutions:**
1. Try a different question
2. Increase K value
3. Check your PDFs are in data/documents/
4. Restart the app

---

## 📄 Adding Your Own Documents

### Where to Put PDFs
```
data/documents/
├── document1.pdf
├── document2.pdf
└── document3.pdf
```

### How to Add
1. Put PDF files in `data/documents/` folder
2. Restart the application
3. Click "Initialize Bot"
4. Wait for processing
5. Ask questions about your documents!

### Tips
- PDFs should be readable (not images)
- PDFs should be in English
- Larger PDFs take longer to process
- Mix of sizes is fine

---

## 🔐 Security & Privacy

### API Keys
- Never share your API key
- Keep in `.env` file only
- `.env` is in .gitignore (not shared)

### Your Data
- Questions are sent to OpenAI
- Answers come from your PDFs + OpenAI
- Conversations saved locally
- Nothing stored permanently on servers

### Best Practices
- Don't ask questions with sensitive info
- Review exports before sharing
- Keep backups of important conversations

---

## 📞 Getting Help

### Something Not Working?
1. Check this guide
2. Check DEPLOYMENT.md for setup
3. Check TESTING_GUIDE.md for troubleshooting
4. Review error messages carefully

### Common Errors
```
"OPENAI_API_KEY not found"
→ Check .env file has your API key

"Port 8501 already in use"
→ Use different port: streamlit run app.py --server.port 8502

"ModuleNotFoundError"
→ Run: pip install -r requirements.txt

"Bot setup failed"
→ Check PDFs are in data/documents/
→ Check API key is valid
→ Check internet connection
```

---

## ✨ Pro Tips

1. **Ask Follow-ups** - Ask multiple related questions in sequence
2. **Check Sources** - Always expand source documents to verify
3. **Adjust Settings** - Try different temperatures for different styles
4. **Use Analytics** - Monitor performance to understand patterns
5. **Export Often** - Save important conversations
6. **Add Documents** - Put all your reference docs in data/documents/
7. **Test First** - Try with sample document before adding yours
8. **Read Errors** - Error messages tell you what's wrong

---

##  Next Steps

### To Learn More
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment
- Read [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing
- Check [README.md](README.md) for technical details

### To Deploy
- Use Streamlit Cloud (free, easiest)
- Use Docker (if you know containers)
- Use AWS/Heroku (for production)

### To Customize
- Edit colors in app.py
- Change temperature defaults in config.py
- Add your PDFs to data/documents/

---

**That's it! Enjoy your RAG Bot! 🎉**
