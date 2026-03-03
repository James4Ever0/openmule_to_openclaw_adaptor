#!/bin/bash

echo "Recommend to use Python 3.11"

# Start Python Backend Script for OpenMule

echo "Starting OpenMule Python Backend..."

# Navigate to backend_python directory
cd backend_python

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    # python3 -m venv venv
    uv venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update the .env file with your configuration before running the server again."
    exit 1
fi

# Start the server
echo "Starting FastAPI server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
