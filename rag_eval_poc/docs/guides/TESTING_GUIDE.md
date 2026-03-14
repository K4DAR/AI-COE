# 🧪 Web UI Testing Guide

## Quick Testing Checklist

### Pre-Flight Check

```bash
# 1. Verify all dependencies
pip list | grep streamlit

# 2. Check Python version
python --version

# 3. Verify .env file
cat .env
# Should show: OPENAI_API_KEY=sk-...
```

### Starting the UI

```bash
# Option 1: Direct run
streamlit run app.py

# Option 2: Debug mode
streamlit run app.py --logger.level=debug

# Option 3: Different port
streamlit run app.py --server.port 8502
```

The app should open automatically at **http://localhost:8501**

---

## Testing Scenarios

###  Test 1: Initial Load

**Steps:**
1. Start the app
2. Browser opens to localhost:8501
3. See "Bot Not Ready" status

**Expected:**
- Page loads quickly
- Sidebar visible on left
- Main content area visible
- No errors in terminal

**Pass Criteria:** ✓ All elements render correctly

---

###  Test 2: Bot Initialization

**Steps:**
1. Click "Initialize Bot" button in sidebar
2. Wait for spinner to complete
3. Status should change to "Bot Ready" 

**Expected:**
- Button becomes clickable
- Spinner shows " Initializing RAG Bot..."
- Status changes to green 
- Takes 3-5 seconds

**Pass Criteria:** ✓ Bot initializes successfully

---

###  Test 3: Ask a Question

**Steps:**
1. Ensure bot is initialized
2. Click on Chat tab
3. Type a question: "What is electricity load forecasting?"
4. Click "Ask" button (or press Enter)

**Expected:**
- Question appears in history
- Spinner shows "🤔 Thinking..."
- Answer appears in 2-4 seconds
- "Source Documents" section appears

**Pass Criteria:** ✓ Question answered with sources shown

---

###  Test 4: View Source Documents

**Steps:**
1. After getting an answer
2. Click "📚 Source Document(s)" expander
3. Review source content

**Expected:**
- Expander shows 3-4 documents
- Each shows source metadata
- Content preview visible

**Pass Criteria:** ✓ Sources display correctly

---

###  Test 5: Clear History

**Steps:**
1. Ask multiple questions (3+)
2. Verify history shows all messages
3. Click "🗑️ Clear History" button
4. Confirm history is empty

**Expected:**
- History clears immediately
- Screen refreshes
- Info message appears

**Pass Criteria:** ✓ History clears correctly

---

###  Test 6: Export Chat

**Steps:**
1. Ask at least one question
2. Click "💾 Export Chat" button
3. Click "📥 Download JSON" button
4. Check downloaded file

**Expected:**
- File downloads as `rag_chat_YYYYMMDD_HHMMSS.json`
- File contains messages and stats
- JSON is valid format

**Pass Criteria:** ✓ Export works and file is valid

---

###  Test 7: Analytics Tab

**Steps:**
1. Ask 3+ questions
2. Switch to "📊 Analytics" tab
3. Verify metrics display

**Expected:**
- Questions count shows number
- Avg response time displays
- Success rate calculated
- Errors count shown

**Pass Criteria:** ✓ Analytics update correctly

---

###  Test 8: Settings Tab

**Steps:**
1. Go to "⚙️ Settings" tab
2. Review displayed configuration
3. Test "🔄 Restart Bot" button

**Expected:**
- Config details visible
- Current settings displayed
- Restart button clears bot

**Pass Criteria:** ✓ Settings display and controls work

---

###  Test 9: Help Tab

**Steps:**
1. Go to "📚 Help" tab
2. Review all sections
3. Verify all text is readable

**Expected:**
- Getting Started section visible
- Tips section visible
- Features section visible
- About RAG section visible

**Pass Criteria:** ✓ Help content displays correctly

---

###  Test 10: Error Handling

**Steps:**
1. Ask invalid question: "a" (1 character)
2. Observe error message
3. Ask question: "What?" (2 words)
4. Observe error or response

**Expected:**
- Invalid input shows error
- Error message clear and helpful
- Input validation working

**Pass Criteria:** ✓ Validation catches bad inputs

---

## Advanced Testing

### Performance Testing

**Measure Response Time:**
```python
import time
start = time.time()
# Ask question
end = time.time()
print(f"Response time: {end - start:.2f}s")
```

**Expected:** 2-4 seconds for answer generation

---

### Stress Testing

**Ask Multiple Questions Rapidly:**
```python
questions = [
    "What is load forecasting?",
    "How does it work?",
    "Why is it important?",
    "What are applications?"
]
for q in questions:
    # Ask each question
    # Measure response time
```

**Expected:** All questions answered without crashes

---

### Configuration Testing

**Test Different Settings:**

```
1. Temperature: 0.1 (focused)
   - Expected: Short, precise answers

2. Temperature: 0.9 (creative)
   - Expected: Longer, more detailed answers

3. K=2 (few docs)
   - Expected: Faster, less context

4. K=8 (many docs)
   - Expected: Slower, more context
```

---

## Browser Testing

### Chrome/Chromium 
```
streamlit run app.py
# Opens in Chrome automatically
```

### Firefox 
```
# Manual: Navigate to localhost:8501
```

### Safari 
```
# Manual: Navigate to localhost:8501
```

### Edge 
```
# Manual: Navigate to localhost:8501
```

---

## Mobile Testing

### Responsive Design

1. Open on mobile browser
2. Check:
   - Sidebar accessible (hamburger menu)
   - Chat interface responsive
   - Buttons clickable
   - Text readable

**Expected:** App is usable on mobile

---

## Security Testing

### API Key Protection

```bash
# Verify API key not in:
grep -r "sk-" app.py  # Should be empty
grep -r "sk-" demo.py  # Should be empty

# Verify .env in .gitignore
cat .gitignore | grep ".env"
```

**Expected:** No API keys in source code

---

## Docker Testing

### Build Docker Image

```bash
docker build -t rag-bot:test .
```

### Run Docker Container

```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-test \
  rag-bot:test
```

**Expected:** App runs in Docker successfully

---

## Docker Compose Testing

```bash
docker-compose up
```

**Expected:** App runs and is accessible at localhost:8501

---

## Test Results Template

Use this to track your tests:

```markdown
## Test Results - [DATE]

### Critical Tests
- [ ] Bot initializes: ✓/✗
- [ ] Question answering: ✓/✗
- [ ] Source display: ✓/✗
- [ ] Error handling: ✓/✗

### Feature Tests
- [ ] Chat history: ✓/✗
- [ ] Analytics: ✓/✗
- [ ] Settings: ✓/✗
- [ ] Export: ✓/✗

### Performance Tests
- [ ] Response time <5s: ✓/✗
- [ ] No memory leaks: ✓/✗
- [ ] Handles 10+ questions: ✓/✗

### Deployment Tests
- [ ] Streamlit Cloud: ✓/✗
- [ ] Docker: ✓/✗
- [ ] Docker Compose: ✓/✗

### Overall Status: ✓ PASS / ✗ FAIL
```

---

## Troubleshooting Common Issues

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "OPENAI_API_KEY not set"

**Solution:**
```bash
# Add to .env
echo OPENAI_API_KEY=sk-your-key > .env

# Or set environment variable
export OPENAI_API_KEY=sk-your-key
```

### Issue: "Port 8501 already in use"

**Solution:**
```bash
streamlit run app.py --server.port 8502
```

### Issue: "Bot initialization fails"

**Solution:**
1. Check API key is valid
2. Check internet connection
3. Check OpenAI service status
4. Review error logs

---

## Performance Benchmarks

### Expected Times

| Operation | Min | Typical | Max |
|-----------|-----|---------|-----|
| Page Load | <1s | 1-2s | 3s |
| Bot Init | 2s | 3s | 5s |
| Doc Retrieval | <1s | 0.5-1s | 2s |
| Answer Gen | 1s | 2-3s | 5s |
| Total Q&A | 2s | 3-4s | 7s |

---

## Success Criteria

 **All tests pass when:**

1. Bot initializes in <5s
2. Questions answered in <5s
3. Sources displayed correctly
4. No errors in console
5. Analytics track correctly
6. Export works
7. Settings apply
8. Mobile responsive
9. No API key exposed
10. Handles 10+ questions

---

**Happy testing! **
