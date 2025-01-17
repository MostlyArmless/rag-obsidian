#!/bin/bash

# Check if parameter is provided
if [ $# -eq 0 ]; then
    echo "Error: Please provide a file path as parameter"
    exit 1
fi

file_path="$1"

# Validate file exists and is readable
if [ ! -f "$file_path" ] || [ ! -r "$file_path" ]; then
    echo "Error: File '$file_path' does not exist or is not readable"
    exit 1
fi

response=$(curl -s -f \
  --request POST \
  --url http://localhost:8080/embed \
  --header 'Content-Type: multipart/form-data' \
  --header 'Accept: application/json' \
  --form "file=@$file_path")

if echo "$response" | jq '.' >/dev/null 2>&1; then
    echo "$response" | jq '.'
else
    echo "Error: Invalid JSON response received:"
    echo "$response"
    exit 1
fi
  