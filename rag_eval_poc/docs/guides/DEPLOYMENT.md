#  RAG Bot Web UI - Deployment Guide

## Overview

The RAG Bot now includes a professional Streamlit web interface that replaces the terminal-based interaction. This guide covers setup, running, and deployment.

## Quick Start

### 1. Install Streamlit

```bash
pip install -r requirements.txt
```

This installs Streamlit along with all other dependencies.

### 2. Run the Web UI

```bash
streamlit run app.py
```

The application will start on `http://localhost:8501`

### 3. Access the UI

Open your browser and navigate to: **http://localhost:8501**

## Features

### 💬 Chat Interface
- **Conversational Q&A**: Ask natural language questions about your documents
- **Real-time Responses**: Get instant answers powered by GPT-4o
- **Source Documents**: View which documents were used to generate answers
- **Conversation History**: All messages are preserved during the session

### 📊 Analytics Dashboard
- **Performance Metrics**: Track questions asked, response times, and error rates
- **Success Rate**: Monitor answer quality
- **Real-time Stats**: Live statistics updates

### ⚙️ Configuration Panel
- **Model Settings**: Adjust temperature and retriever parameters
- **Document Settings**: Configure chunk size and overlap
- **Validation Rules**: View input/output constraints
- **Bot Control**: Restart bot or reset statistics

### 📚 Help & Documentation
- **Getting Started**: Quick tutorial
- **Tips & Tricks**: Best practices
- **Features Overview**: Complete feature list
- **About RAG**: Educational content

### 💾 Export Options
- **Chat Export**: Download conversations as JSON
- **History Management**: Clear history or save sessions
- **Session Tracking**: Persistent statistics

## Project Structure

```
rag_eval_poc/
├── app.py                           # Main Streamlit application
├── .streamlit/
│   └── config.toml                  # Streamlit configuration
├── config.py                        # Configuration management
├── validators.py                    # Input/output validation
├── demo.py                          # RAG bot logic
├── rag/
│   ├── loader.py                    # Document loading
│   ├── vector_store.py              # Vector store management
│   └── rag_chain.py                 # RAG chain implementation
├── evaluation/
│   ├── run_eval.py                  # Evaluation framework
│   └── test_cases.yaml              # Test cases
├── data/
│   └── documents/                   # PDF documents
├── requirements.txt                 # Python dependencies
├── README.md                        # Main documentation
├── DEPLOYMENT.md                    # This file
└── START_HERE.md                    # Quick start guide
```

## Configuration

### Streamlit Config (.streamlit/config.toml)

The configuration file controls:
- **Theme**: Colors and appearance
- **Client**: UI settings
- **Server**: Port and security
- **Browser**: Analytics and tracking

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
CHROMA_DB_PATH=./chroma_db
PDF_CHUNK_SIZE=500
PDF_CHUNK_OVERLAP=50
```

## Deployment Options

### Option 1: Local Development

```bash
streamlit run app.py
```

Perfect for:
- Local testing
- Development
- Small team collaboration

### Option 2: Streamlit Cloud (Recommended)

**Free cloud hosting by Streamlit**

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Click Deploy

```yaml
# Add secrets in Streamlit Cloud dashboard
openai_api_key: sk-your-api-key
```

### Option 3: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p data/documents chroma_db .streamlit

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
# Build image
docker build -t rag-bot:latest .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=sk-your-api-key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/chroma_db:/app/chroma_db \
  rag-bot:latest
```

### Option 4: Heroku Deployment

Create `Procfile`:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

Create `runtime.txt`:

```
python-3.11.4
```

Deploy:

```bash
heroku login
heroku create your-app-name
heroku config:set OPENAI_API_KEY=sk-your-api-key
git push heroku main
```

### Option 5: AWS Deployment

Using EC2:

1. Launch an EC2 instance (Ubuntu 22.04)
2. Connect via SSH
3. Install dependencies:

```bash
sudo apt update
sudo apt install python3-pip python3-venv
git clone your-repo
cd rag-eval-poc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Run with systemd:

```bash
sudo nano /etc/systemd/system/rag-bot.service
```

```ini
[Unit]
Description=RAG Bot Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/rag-eval-poc
Environment="PATH=/home/ubuntu/rag-eval-poc/venv/bin"
Environment="OPENAI_API_KEY=sk-your-api-key"
ExecStart=/home/ubuntu/rag-eval-poc/venv/bin/streamlit run app.py --server.port=80 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl start rag-bot
sudo systemctl enable rag-bot
```

## Performance Optimization

### 1. Caching

The app uses Streamlit's caching for:
- Bot initialization
- Vector store loading
- Document processing

```python
@st.cache_resource
def get_bot():
    return RAGBotDemo()
```

### 2. Session State

Persistent state across reruns:
- Conversation history
- Statistics
- Bot instance
- Current document

### 3. Lazy Loading

Components load on demand:
- Analytics only when tab is selected
- Settings parsed on request
- Sources expanded on user action

## Security Considerations

### API Key Management

**Never commit API keys!**

1. **Local Development**:
   ```bash
   # Add to .gitignore
   .env
   .streamlit/secrets.toml
   ```

2. **Environment Variables**:
   ```bash
   export OPENAI_API_KEY=sk-your-api-key
   streamlit run app.py
   ```

3. **Streamlit Secrets**:
   - In Streamlit Cloud: Dashboard → Settings → Secrets
   - Locally: `.streamlit/secrets.toml` (never commit)

### Input Validation

All inputs are validated:
- Question length checks
- Character validation
- Injection prevention
- Error handling

### Error Handling

User-friendly error messages:
- No stack traces to users
- Logging for debugging
- Graceful error recovery

## Troubleshooting

### Issue: "ModuleNotFoundError"

```bash
# Ensure all packages installed
pip install -r requirements.txt

# Verify environment
pip list | grep streamlit
```

### Issue: "OPENAI_API_KEY not found"

```bash
# Check environment variable
echo $OPENAI_API_KEY

# Set if missing
export OPENAI_API_KEY=sk-your-api-key

# Or create .env file
echo "OPENAI_API_KEY=sk-your-api-key" > .env
```

### Issue: "Port already in use"

```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Issue: "Slow response times"

1. Check internet connection
2. Verify OpenAI API status
3. Reduce chunk size in config
4. Clear browser cache

## Monitoring

### Logs

View Streamlit logs:

```bash
# Terminal shows all logs
streamlit run app.py --logger.level=debug
```

View application logs:

```bash
# Check demo.py logs
tail -f logs/rag_bot.log
```

### Metrics

Access built-in analytics:
- Questions processed
- Response times
- Error rates
- Success rate

## Advanced Configuration

### Custom CSS

Modify styling in `app.py`:

```python
st.markdown("""
    <style>
    /* Your custom CSS */
    </style>
""", unsafe_allow_html=True)
```

### Custom Components

Add new Streamlit components:

```bash
pip install streamlit-component-name
```

### API Integration

Connect external services:

```python
import requests

response = requests.get("https://api.example.com/data")
```

## Performance Benchmarks

Typical response times (on a standard machine):

- **Bot Initialization**: 2-5 seconds
- **Document Processing**: 5-10 seconds (depends on PDF size)
- **Answer Generation**: 2-4 seconds
- **Source Retrieval**: <1 second

## Scaling

For production use with many users:

1. **Use Streamlit Cloud**: Automatic scaling
2. **Implement caching**: Reduce API calls
3. **Use backend API**: Separate FastAPI server
4. **Database**: Persistent chat history
5. **Load balancing**: Multiple instances

## Support & Resources

- **Documentation**: See [START_HERE.md](START_HERE.md)
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **LangChain Docs**: [python.langchain.com](https://python.langchain.com)
- **OpenAI Docs**: [platform.openai.com/docs](https://platform.openai.com/docs)

## Next Steps

1.  Run the web UI locally
2.  Test with your documents
3.  Configure OpenAI settings
4.  Choose a deployment platform
5.  Deploy to production

---

**Happy deploying! **
