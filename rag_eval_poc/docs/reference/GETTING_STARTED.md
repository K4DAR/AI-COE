# RAG Bot - Getting Started Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Edit `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Run the Bot
```bash
# Interactive mode
python demo.py

# Single question
python demo.py --question "What is load forecasting?"
```

## Commands & Options

### Interactive Mode
```bash
python demo.py
```
- Type questions naturally
- Type `exit` or `quit` to quit
- Type `stats` to see statistics
- Type `help` for more options

### Single Question
```bash
python demo.py --question "Your question here?"
```

### Reset & Rebuild
```bash
python demo.py --reset --pdf data/documents/sample_doc.pdf
```

### Use Custom PDF
```bash
python demo.py --pdf path/to/your/document.pdf
```

## Evaluation

Run evaluation against test cases:
```bash
python evaluation/run_eval.py
```

Results saved to: `evaluation/evaluation_results.json`

## Project Structure

```
rag_eval_poc/
├── config.py              # Configuration settings
├── validators.py          # Input/output validation
├── demo.py               # Main bot application
├── validate_system.py    # System validation
├── setup.py              # Setup script
├── create_sample_pdf.py  # PDF creation utility
├── README.md             # Full documentation
├── requirements.txt      # Python dependencies
├── .env                  # API keys (create this)
│
├── data/
│   └── documents/        # PDF files directory
│
├── rag/
│   ├── __init__.py
│   ├── loader.py        # Document loading
│   ├── vector_store.py  # Vector storage
│   └── rag_chain.py     # RAG chain logic
│
└── evaluation/
    ├── run_eval.py      # Evaluation script
    ├── test_cases.yaml  # Test cases
    └── evaluation_results.json  # Results (generated)
```

## Configuration

Edit `config.py` to customize:

```python
# Document processing
PDF_CHUNK_SIZE = 800           # Size of text chunks
PDF_CHUNK_OVERLAP = 100        # Overlap between chunks

# Model settings
OPENAI_MODEL = "gpt-4o"        # LLM to use
OPENAI_TEMPERATURE = 0         # Deterministic (0) to creative (1)

# Retrieval
RETRIEVER_K = 3                # Number of documents to retrieve

# Validation
MIN_QUESTION_LENGTH = 3        # Minimum question length
MAX_QUESTION_LENGTH = 500      # Maximum question length
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'langchain'"
```bash
pip install -r requirements.txt
```

### "OPENAI_API_KEY not set"
1. Create/edit `.env` file
2. Add: `OPENAI_API_KEY=sk-your-key-here`
3. Restart the application

### "Vector store not found"
The system needs to build the vector store from your PDF:
```bash
python demo.py --reset --pdf data/documents/sample_doc.pdf
```

### "No chunks created from documents"
- Your PDF may be corrupted
- Try a different PDF file
- Check PDF has extractable text

## Features

✓ **Validation**: Input and output validation  
✓ **Error Handling**: Comprehensive error messages  
✓ **Logging**: Detailed execution logs  
✓ **Retrieval**: Source document tracking  
✓ **Evaluation**: Built-in test metrics  
✓ **Configuration**: Easy customization  
✓ **Documentation**: Full README included  

## Example Session

```
$ python demo.py

================================================================================
🤖 RAG BOT - Interactive Mode
================================================================================
Type 'exit' or 'quit' to end conversation
Type 'stats' to see bot statistics
================================================================================

❓ Ask a question: What is electricity load forecasting?

================================================================================
📝 ANSWER:
================================================================================
Electricity load forecasting is the process of predicting future electricity 
demand based on historical data and various influencing factors...

================================================================================
📚 SOURCES:
================================================================================

1. Source: data/documents/sample_doc.pdf
   Page: 1
   Content preview: Electricity load forecasting is the process of predicting...
```

## Next Steps

1. **Test the System**: `python validate_system.py`
2. **Ask Questions**: `python demo.py`
3. **Run Evaluation**: `python evaluation/run_eval.py`
4. **Add Documents**: Put PDFs in `data/documents/`
5. **Customize Tests**: Edit `evaluation/test_cases.yaml`

## Performance Tips

- **Faster responses**: Reduce `RETRIEVER_K` to 1-2
- **Better accuracy**: Increase `RETRIEVER_K` to 5-10
- **Faster indexing**: Increase `PDF_CHUNK_SIZE` to 1500
- **Better retrieval**: Decrease `PDF_CHUNK_SIZE` to 400

## API Keys

🔒 **Security**: Never commit `.env` to version control!

```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

## Support

- Check logs in the terminal output
- Review error messages for hints
- See `README.md` for full documentation
- Run `validate_system.py` to diagnose issues

## For More Information

See `README.md` for:
- Detailed API documentation
- Advanced configuration
- Custom validation rules
- Development guidelines
