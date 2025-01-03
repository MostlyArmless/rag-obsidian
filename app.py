import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify
from embed import embed
from query import query
from get_vector_db import get_vector_db
TEMP_FOLDER = os.getenv("TEMP_FOLDER", './_temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = Flask(__name__)

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

@app.route('/embed', methods=['POST'])
def route_embed():
  if 'file' not in request.files:
    return jsonify({'error': 'No file part'}), 400
  
  file = request.files['file']

  if file.filename == '':
    return jsonify({'error': 'No selected file'}), 400
  
  embedded = embed(file)

  if embedded:
    return jsonify({"message": "File embedded successfullly"}), 200
  
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

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8080, debug=True)