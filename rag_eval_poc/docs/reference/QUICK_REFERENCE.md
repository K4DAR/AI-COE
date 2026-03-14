# RAG Bot - Quick Reference Card

##  5-Minute Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure  
echo "OPENAI_API_KEY=sk-your-key" > .env

# 3. Run
python demo.py
```

## 📋 Common Commands

| Command | Purpose |
|---------|---------|
| `python demo.py` | Interactive mode |
| `python demo.py --question "Q?"` | Single question |
| `python demo.py --reset --pdf file.pdf` | Rebuild vector store |
| `python evaluate/run_eval.py` | Run evaluation |
| `python validate_system.py` | Check system |
| `python create_sample_pdf.py` | Create sample PDF |

## ⚙️ Key Configuration Settings

| Setting | Default | Purpose |
|---------|---------|---------|
| `PDF_CHUNK_SIZE` | 800 | Document chunk size |
| `RETRIEVER_K` | 3 | Documents to retrieve |
| `OPENAI_MODEL` | gpt-4o | LLM model |
| `OPENAI_TEMPERATURE` | 0 | Response determinism |
| `MIN_QUESTION_LENGTH` | 3 | Question validation |
| `MAX_QUESTION_LENGTH` | 500 | Question validation |

## 🗂️ File Structure Quick Guide

```
rag_eval_poc/
├── demo.py              → Run this
├── config.py            → Edit this to customize
├── validators.py        → Validation logic
├── .env                 → Add API key here
└── rag/                 → RAG modules (don't edit)
```

## 🔍 Validation Rules at a Glance

### Questions
- ✓ 3-500 characters
- ✓ Must contain letters/numbers
- ✗ Empty or too short/long

### Answers
- ✓ 10-5000 characters
- ✓ Generated from documents
- ✗ Empty or too short

### Files
- ✓ PDF, TXT, MD
- ✓ Max 100MB
- ✗ Corrupted or unreadable

## 🐛 Troubleshooting Matrix

| Problem | Solution |
|---------|----------|
| API key error | Add `OPENAI_API_KEY` to `.env` |
| Module not found | Run `pip install -r requirements.txt` |
| Vector store missing | Run `python demo.py --reset --pdf file.pdf` |
| Import errors | Run `python validate_system.py` |
| Slow responses | Reduce `RETRIEVER_K` in `config.py` |

## 📊 Interactive Mode Commands

```
❓ Ask a question: What is load forecasting?
  → Answers from documents with sources

❓ Ask a question: stats
  → Shows statistics

❓ Ask a question: exit
  → Quits the bot
```

## 🔐 Security Checklist

- [ ] `.env` added to `.gitignore`
- [ ] API key never hardcoded
- [ ] `.env` never committed
- [ ] Secrets in environment variables

## 📝 Logging Levels

```python
# config.py
LOG_LEVEL = "INFO"      # Production (default)
LOG_LEVEL = "DEBUG"     # Development/troubleshooting
```

## 💾 Configuration Examples

### Faster Responses
```python
RETRIEVER_K = 1
PDF_CHUNK_SIZE = 1500
```

### Better Quality
```python
RETRIEVER_K = 5
PDF_CHUNK_SIZE = 400
```

### Creative Answers
```python
OPENAI_TEMPERATURE = 0.7
```

### Strict Answers
```python
OPENAI_TEMPERATURE = 0
```

## 🧪 System Check

```bash
python validate_system.py
```

Checks:
- ✓ File structure
- ✓ Dependencies
- ✓ Configuration
- ✓ Sample PDF
- ✓ All modules importable

## 📖 Documentation Map

| File | Contents |
|------|----------|
| README.md | Full reference |
| GETTING_STARTED.md | Quick start guide |
| PROJECT_SUMMARY.md | Project overview |
| This file | Quick reference |

## 🎯 Typical Workflow

```bash
# Day 1: Setup
pip install -r requirements.txt
echo "OPENAI_API_KEY=..." > .env
python validate_system.py          # Should pass ✓
python demo.py                     # Try interactive mode

# Day 2+: Use
python demo.py --question "Your question?"
python evaluation/run_eval.py      # Test quality
```

## 🚨 Critical Files

| File | If Missing |
|------|-----------|
| `.env` | Add `OPENAI_API_KEY` |
| `requirements.txt` | Run `pip install` |
| `config.py` | System won't start |
| `rag/` folder | Core RAG missing |

## ✨ Pro Tips

1. **Add your own PDFs**: Put in `data/documents/` then run `python demo.py --reset`
2. **Customize questions**: Edit `evaluation/test_cases.yaml`
3. **Check logs**: Add `LOG_LEVEL = "DEBUG"` in config.py
4. **Track costs**: Monitor OpenAI API usage
5. **Improve quality**: Adjust `RETRIEVER_K` and chunk sizes

## 🔗 External Resources

- OpenAI API: https://platform.openai.com
- LangChain Docs: https://python.langchain.com
- ChromaDB: https://www.trychroma.com
- DeepEval: https://github.com/confident-ai/deepeval

---

**Print this for quick reference! 📌**
