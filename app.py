import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify
from embed import embed
from query import query
from chromadb.utils import embedding_functions
from chromadb import Client

TEMP_FOLDER = os.getenv("TEMP_FOLDER", './_temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = Flask(__name__)
chroma_client = Client()

def init_chroma_db():
    """Initialize Chroma DB schema on app startup"""
    COLLECTION_NAME = "documents"
    
    try:
        collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Document embeddings for RAG system"}
        )
        print(f"Initialized collection: {COLLECTION_NAME}")
        return collection
    except Exception as e:
        print(f"Fatal error initializing Chroma DB: {e}")
        raise e

# Initialize DB when app starts
documents_collection = init_chroma_db()

def log_query(request_text, response_text):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "request": request_text,
        "response": response_text
    }
    
    try:
        # Read existing logs
        try:
            with open('queries.json', 'r') as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []
        
        # Append new entry
        logs.append(log_entry)
        
        # Write back to file
        with open('queries.json', 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Error logging query: {e}")

def debug_chroma_db():
    """Debug function to print Chroma DB state"""
    print("\n=== Chroma DB Debug Info ===")
    
    # List all collections
    collections = chroma_client.list_collections()
    print(f"\nTotal collections: {len(collections)}")
    
    if len(collections) == 0:
        print("No collections found - DB is empty")
        return
        
    # Print details for each collection
    for collection in collections:
        print(f"\nCollection: {collection.name}")
        try:
            count = collection.count() # type: ignore
            print(f"Documents count: {count}")
            if count > 0:
                # Get sample document to see metadata structure
                first_doc = collection.get(limit=1)
                print("Metadata structure:", first_doc['metadatas'][0] if first_doc['metadatas'] else "No metadata")
        except Exception as e:
            print(f"Error accessing collection: {e}")

@app.route('/embed', methods=['POST'])
def route_embed():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check if file already embedded
    existing = documents_collection.get(
        where={"filename": file.filename or ""}
    )
    
    if existing and len(existing['ids']) > 0:
        return jsonify({"message": "File has previously been embedded, skipping"}), 304
    
    embedded = embed(file)
    if embedded:
        return jsonify({"message": "File embedded successfully"}), 200
    
    return jsonify({"error": "Failed to embed file"}), 500

@app.route('/query', methods=['POST'])
def route_query():
  data = request.get_json()
  request_text = data.get('query')
  response = query(request_text)

  if response:
    log_query(request_text, response)
    return jsonify(response), 200
  
  return jsonify({"error": "Failed to query"}), 500

@app.route('/debug/reset-db', methods=['POST'])
def reset_db():
    collections = chroma_client.list_collections()
    for collection in collections:
        chroma_client.delete_collection(collection.name)
    return jsonify({"message": "Database reset complete"}), 200

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8080, debug=True)