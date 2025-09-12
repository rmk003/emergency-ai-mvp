#!/bin/bash

echo "🛡️ Starting RideGuard Emergency AI Assistant MVP..."
echo "================================================"

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo "📋 Installing dependencies..."
pip install -r requirements.txt

echo "🔧 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating template..."
    cp .env .env.template
fi

echo "🚀 Starting FastAPI server..."
echo "📱 Demo will be available at: http://localhost:8000"
echo "🔗 API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py