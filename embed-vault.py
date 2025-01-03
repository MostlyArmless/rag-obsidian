from langchain_community.document_loaders import ObsidianLoader
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma

# Load Obsidian documents
loader = ObsidianLoader("<path-to-obsidian>")
docs = loader.load()[5]

# Create embeddings using Ollama
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Create vector store
vectorstore = Chroma.from_documents(docs, embeddings)
