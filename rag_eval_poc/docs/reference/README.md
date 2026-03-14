# RAG Bot with Validation and Evaluation

A production-ready Retrieval-Augmented Generation (RAG) bot with comprehensive validation, error handling, evaluation metrics, and a **professional web UI**.

## 🌟 Key Features

### 🤖 Core RAG System
- **Document Loading**: Load and process PDF documents with configurable chunking
- **Vector Store**: ChromaDB for efficient semantic document retrieval
- **RAG Chain**: LangChain-based question-answering with source tracking
- **GPT-4o Integration**: Powered by OpenAI's latest model

### 🌐 Professional Web UI
- **Modern Streamlit Interface**: Clean, professional chat interface
- **Real-time Analytics**: Track questions, response times, and accuracy
- **Chat History**: Persistent conversation tracking
- **Source Documents**: View documents used for answers
- **Export Functionality**: Download conversations as JSON
- **Configuration Panel**: Adjust model parameters on the fly

###  Quality & Validation
- **Input Validation**: Validate questions for quality and length
- **Output Validation**: Validate answers for completeness
- **Error Handling**: Comprehensive error handling with detailed logging
- **Evaluation Metrics**: Built-in evaluation with DeepEval integration

##  Quick Start

### Option 1: Web UI (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web app
streamlit run app.py
```

Open your browser to: **http://localhost:8501**

### Option 2: Terminal (Traditional)

```bash
python demo.py
```

Choose "interactive" mode for Q&A or provide a question via command line.

## Project Structure

```
rag_eval_poc/
├── app.py                          # Streamlit web UI (NEW!)
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── config.py                       # Configuration management
├── validators.py                   # Input/output validation
├── demo.py                         # Main demo with interactive mode
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose setup
├── setup.sh / setup.bat            # Setup scripts
├── data/
│   └── documents/                  # PDF documents directory
├── rag/
│   ├── loader.py                   # Document loading and chunking
│   ├── vector_store.py             # Vector store management
│   └── rag_chain.py                # RAG chain creation
├── evaluation/
│   ├── run_eval.py                 # Evaluation runner
│   └── test_cases.yaml             # Test cases for evaluation
└── notebooks/
    └── exploration.ipynb           # Jupyter notebooks
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- OpenAI API Key
- Virtual environment (recommended)

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 3. Configure Environment

Create or update `.env` file with your API keys:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 4. Add Documents

Place your PDF files in `data/documents/` directory:

```bash
# Example
cp your_document.pdf data/documents/sample_doc.pdf
```

## Usage

### Interactive Mode

Run the bot in interactive mode to ask multiple questions:

```bash
python demo.py
```

Features:
- Type your questions naturally
- View answers with source documents
- Type 'exit' or 'quit' to quit
- Type 'stats' to see statistics

### Single Question Mode

Ask a single question from command line:

```bash
python demo.py --question "What is electricity load forecasting?"
```

### Reset Vector Store

Delete existing vector store and rebuild from PDF:

```bash
python demo.py --reset --pdf data/documents/sample_doc.pdf
```

### Use Custom PDF

Load a different PDF file:

```bash
python demo.py --pdf path/to/your/document.pdf
```

## Evaluation

### Run Evaluation

Evaluate the bot against test cases:

```bash
python evaluation/run_eval.py
```

Options:
- `--test-cases path/to/test_cases.yaml` - Custom test cases file
- `--output path/to/results.json` - Save results to custom location
- `--skip-deepeval` - Skip DeepEval metrics

### Test Cases Format

Test cases are defined in YAML format (`evaluation/test_cases.yaml`):

```yaml
- question: "What is electricity load forecasting?"
  expected_answer: "Electricity load forecasting predicts future electricity demand based on historical data."
  context: "Page 2 - definition of load forecasting"
  type: straightforward

- question: "What factors affect electricity demand?"
  expected_answer: "Weather, population, economic activity and seasonality."
  context: "Page 4 demand factors"
  type: tricky

- question: "What is the capital of Japan?"
  expected_answer: "Not in document"
  context: "Not in documents"
  type: unanswerable
```

### Evaluation Metrics

The evaluation framework includes:

1. **HallucinationMetric**: Detects false information in responses
2. **FaithfulnessMetric**: Measures how faithful answers are to source documents
3. **AnswerRelevancyMetric**: Evaluates how relevant answers are to questions
4. **ContextualRecallMetric**: Measures how well retrieval captures relevant information

Results are saved to `evaluation/evaluation_results.json`.

## Configuration

Edit `config.py` to customize:

```python
# Document Processing
PDF_CHUNK_SIZE = 800              # Size of document chunks
PDF_CHUNK_OVERLAP = 100           # Overlap between chunks

# Validation
MIN_QUESTION_LENGTH = 3           # Minimum question length
MAX_QUESTION_LENGTH = 500         # Maximum question length
MIN_ANSWER_LENGTH = 10            # Minimum answer length
MAX_ANSWER_LENGTH = 5000          # Maximum answer length

# LLM
OPENAI_MODEL = "gpt-4o"           # Model to use
OPENAI_TEMPERATURE = 0            # Temperature for deterministic answers

# Retrieval
RETRIEVER_K = 3                   # Number of documents to retrieve

# Vector Store
VECTOR_STORE_TYPE = "chroma"      # Vector store type
```

## Logging

Logs are configured to show:
- INFO: General information about processing
- DEBUG: Detailed processing steps
- ERROR: Error messages with stack traces
- WARNING: Warnings and issues

Set log level in `config.py`:
```python
LOG_LEVEL = "INFO"  # Change to DEBUG for more details
```

## Error Handling

The system includes comprehensive error handling for:

- Invalid file paths
- Missing or corrupted documents
- Invalid user input
- API failures
- Vector store issues
- Configuration errors

Errors are logged with full context and displayed to users clearly.

## Validation

### Input Validation
- Question length (3-500 characters)
- Non-empty questions
- Alphanumeric content

### Output Validation
- Answer length (10-5000 characters)
- Non-empty responses
- Confidence scores (0-1)

### File Validation
- File existence
- File type (.pdf, .txt, .md)
- File size (max 100MB)

## Troubleshooting

### "Vector store not found"
```bash
# Rebuild vector store
python demo.py --reset --pdf data/documents/sample_doc.pdf
```

### "OPENAI_API_KEY is not set"
```bash
# Make sure .env file has your API key
echo "OPENAI_API_KEY=your-key-here" > .env
```

### "No chunks created from documents"
- Verify PDF file is not corrupted
- Check that PDF has extractable text
- Try with a different PDF file

### Slow responses
- Reduce `RETRIEVER_K` in config.py
- Use a faster embedding model
- Check OpenAI API status

## Advanced Usage

### Custom Evaluation Metrics

Extend `validators.py` to add custom validation logic:

```python
class CustomValidator:
    @staticmethod
    def validate_domain_specific(answer: str) -> Tuple[bool, str]:
        # Your custom validation logic
        pass
```

### Notebook Exploration

Use `notebooks/exploration.ipynb` to:
- Explore document chunks
- Test retrieval quality
- Visualize embeddings
- Analyze evaluation results

## Performance Tips

1. **Smaller Chunks**: Reduce `PDF_CHUNK_SIZE` for more precise retrieval
2. **More Context**: Increase `RETRIEVER_K` for broader context
3. **Temperature**: Set to 0 for deterministic answers
4. **Caching**: Vector store is persisted, eliminating re-embedding

## API Keys Management

**Security Warning**: Never commit `.env` file to version control!

```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

Store sensitive keys in:
- Environment variables
- Secrets management systems
- CI/CD secret stores

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:
1. Check logs in the terminal output
2. Review error messages and suggestions
3. Verify configuration in `config.py`
4. Test with different documents or questions
