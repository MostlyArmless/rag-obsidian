# rag-obsidian

The purpose of this repo is to set up my own personal RAG-based query system for my Obsidian vault.

## Setup

```bash
venv
pip install -r requirements.txt
```

## Usage

```bash
# Run the Flask server
python app.py

# Embed a file:
./embed.sh /path/to/file.pdf # Currently only supports PDFs, and they should contain text not images of text

# Query the server
./query.sh "What is the capital of France?"
```
