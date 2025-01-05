from typing import List
from langchain_community.document_loaders import ObsidianLoader
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain.vectorstores import Chroma
from os import getenv, path


class CustomObsidianLoader(ObsidianLoader):
  # Override the lazy_load method to allow us to specify either a blacklist or whitelist of files to load
  def lazy_load(self, blacklist: List[str] | None = None, whitelist: List[str] | None = None):
    paths = list(path(self.file_path).glob("**/*.md"))
    for path in paths:
      if blacklist and path in blacklist:
        continue
      if whitelist and path not in whitelist:
        continue
      with open(path, encoding=self.encoding) as f:
        text = f.read()
      
      front_matter = self._parse_front_matter(text)
      tags = self._parse_document_tags(text)
      dataview_fields = self._parse_dataview_fields(text)
      text = self._remove_front_matter(text)
      yield Document(
        page_content=text,
        metadata={
          "front_matter": front_matter,
          "tags": tags,
          "dataview_fields": dataview_fields
        }
      )


# Load Obsidian documents
vault_path = getenv("OBSIDIAN_VAULT_PATH")

if not vault_path or not path.isdir(vault_path):
  raise ValueError(f"Invalid or missing OBSIDIAN_VAULT_PATH: '{vault_path}'")

# Loads only markdown files, not media or PDFs
blacklist = ["_notion-like-tables/", "Excalidraw/", 'MEDIA/', 'lib/', 'TEMPLATES/', 'File Transfer/']
loader = CustomObsidianLoader(vault_path, whitelist=[])
docs = loader.load()

# Create embeddings using Ollama
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Create vector store
vectorstore = Chroma.from_documents(docs, embeddings)
