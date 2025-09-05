# A series of crawl scripts to scrape data from anywhere

## Setup

### 1. Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Start Ollama Service
```bash
ollama serve
```

### 3. Pull the Model
```bash
ollama pull llama3.2
```

### 4. Install Python Dependencies
```bash
pip install -r ollama_requirements.txt
```

## Running the Script

```bash
python deepcrawl.py
```

## Stopping Ollama service:
```bash
pkill ollama
```