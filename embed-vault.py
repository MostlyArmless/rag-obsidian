from typing import Set
from langchain_community.document_loaders import ObsidianLoader
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata
from pathlib import Path
from os import getenv, path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

from get_vector_db import get_vector_db

class CustomObsidianLoader(ObsidianLoader):
  def __init__(self, path: str | Path, encoding: str = "UTF-8", collect_metadata: bool = True, blacklist: Set[str] | None = None, whitelist: Set[str] | None = None):
    super().__init__(path, encoding, collect_metadata)
    self.blacklist = blacklist
    self.whitelist = whitelist

  def lazy_load(self):
    paths = list(Path(self.file_path).glob("**/*.md"))
    for path in paths:
      if self.blacklist and path in self.blacklist:
        print(f"Skipping blacklisted {path}")
        continue
      if self.whitelist and path not in self.whitelist:
        print(f"Skipping non-whitelisted {path}")
        continue
      print(f"Loading {path}")
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
load_dotenv()
vault_path = getenv("OBSIDIAN_VAULT_PATH")

if not vault_path or not path.isdir(vault_path):
  raise ValueError(f"Invalid or missing OBSIDIAN_VAULT_PATH: '{vault_path}'")

# Loads only markdown files, not media or PDFs
# blacklist = set(["_notion-like-tables/", "Excalidraw/", 'MEDIA/', 'lib/', 'TEMPLATES/', 'File Transfer/'])
# whitelist = set(["Work/Foodee/"])
loader = CustomObsidianLoader(vault_path)#, blacklist=blacklist, whitelist=whitelist)
print('Loading documents...')
docs = loader.load()

# Convert complex metadata types to strings
filtered_docs = filter_complex_metadata(docs)
# # Convert remaining dict values to strings
# for filtered_doc in filtered_docs:
#     filtered_doc.metadata = {k: str(v) for k, v in filtered_doc.metadata.items()}


# print('Chunking documents...')
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
# chunks = []
# for doc in docs:
#   chunks.extend(text_splitter.split_text(doc.page_content))

# Store embeddings in Chroma
print('Computing and storing embeddings...')
db = get_vector_db()
db.add_documents(filtered_docs)
db.persist()

print('Done!')