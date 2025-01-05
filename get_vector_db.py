import os
from threading import Lock
from langchain_ollama import OllamaEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()
CHROMA_PATH = os.getenv('CHROMA_PATH', 'chroma')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'rag-obsidian')
TEXT_EMBEDDING_MODEL = os.getenv('TEXT_EMBEDDING_MODEL', 'nomic-embed-text')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

_db_instance = None
_db_lock = Lock()

def get_vector_db():
    """Singleton pattern to get the vector database instance"""

    global _db_instance
    
    if _db_instance is None:
        with _db_lock:
            if _db_instance is None:
                embedding = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL, base_url=OLLAMA_HOST)
                _db_instance = Chroma(
                    collection_name=COLLECTION_NAME,
                    persist_directory=CHROMA_PATH,
                    embedding_function=embedding
                )
    
    return _db_instance