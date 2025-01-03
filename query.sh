#!/bin/bash

# Check if parameter is provided
if [ $# -eq 0 ]; then
    echo "Error: Please provide a query string"
    echo "Usage: ./query.sh \"your question here\""
    exit 1
fi

# Escape quotes in the query parameter
query=$(echo "$1" | sed 's/"/\\"/g')

curl --request POST \
  --url http://localhost:8080/query \
  --header 'Content-Type: application/json' \
  --data "{\"query\": \"$query\"}"