# rag-obsidian

The purpose of this repo is to set up my own personal RAG-based query system for my Obsidian vault.

Starting out with the content of [this tutorial](https://www.gpu-mart.com/blog/how-to-build-local-rag-app-with-langchain-ollama-python-and-chroma) to learn how a basic RAG setup works.

The goal is to have a server that can embed files from my Obsidian vault, and let me query them using a RAG model.

## Roadmap and requirements

* Support for embedding markdown and PDF files
* curl `/embed` to embed a single file
* curl `/query` to query the RAG model
* cronjob to periodically check the git repo for the Obsidian vault to see if there are any new files to embed, and embed them
* MVP = embed a manually-specified list of files
  * Part 2 = specify a blacklist of filetypes and directories to ignore and auto-embed everything else
  * Part 3 = when embedding files, keep track of the path in the vault and the timestamp of the last update
* allow deletion of files from the vector DB
* allow updating of files in the vector DB
* allow listing of all embedded files

## Setup

```bash
venv
pip install -r requirements.txt
```

## Usage

### Flask Server for individual embedding and querying

```bash
venv

# Run the Flask server
python app.py

# Embed a file:
./embed.sh /path/to/file.pdf # Currently only supports PDFs, and they should contain text not images of text

# Query the server
./query.sh "What is the capital of France?"
```

### Script for auto-embedding the entire Obsidian vault

```bash
venv

# Embed all files in the Obsidian vault
python embed-vault.py

# Query against that chroma DB
python query.py "What is the capital of France?"
```