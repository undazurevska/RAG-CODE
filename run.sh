#!/bin/bash

echo "🐍 Creating virtual environment (if missing)..."
python3 -m venv .venv
source .venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🧠 Starting Ollama in background..."
ollama serve > /dev/null 2>&1 &

echo "🚀 Running RAG Slackbot..."
python3 -m backend.app