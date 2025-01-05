import os
from datetime import datetime
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from get_vector_db import get_vector_db

TEMP_FOLDER = os.getenv('TEMP_FOLDER', './_temp')

# Function to check if the uploaded file is allowed (only PDF files)
supported_filetypes = set(['pdf', 'md'])
def get_supported_filetype(filename: str) -> str | None:
    if '.' not in filename:
        return None
    extension = filename.rsplit('.', 1)[1].lower()
    return extension if extension in supported_filetypes else None

# Function to save the uploaded file to the temporary folder
def save_file(file):
    # Save the uploaded file with a secure filename and return the file path
    ct = datetime.now()
    ts = ct.timestamp()
    filename = str(ts) + "_" + secure_filename(file.filename)
    file_path = os.path.join(TEMP_FOLDER, filename)
    file.save(file_path)

    return file_path

# Function to load and split the data from the PDF file
def load_and_split_pdf(file_path):
    # Load the PDF file and split the data into chunks
    loader = UnstructuredPDFLoader(file_path=file_path)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)

    return chunks

# Function to load and split data from markdown files:
def load_and_split_markdown(file_path):
    # Load the markdown file and split the data into chunks
    loader = UnstructuredMarkdownLoader(file_path=file_path)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)

    return chunks

# Main function to handle the embedding process
def embed(file):
    # Check if the file is valid, save it, load and split the data, add to the database, and remove the temporary file
    if file.filename != '' and file:
        chunks = None

        filetype = get_supported_filetype(file.filename)
        if filetype is None:
            return False
        
        file_path = save_file(file)
        if filetype == 'pdf':
            chunks = load_and_split_pdf(file_path)
        elif filetype == 'md':
            chunks = load_and_split_markdown(file_path)

        if chunks is not None:
            db = get_vector_db()
            db.add_documents(chunks)
            db.persist()
            os.remove(file_path)
            return True

    return False