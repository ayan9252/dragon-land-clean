#!/bin/bash

echo "🚀 Dragon Land Server - Starting Auto Deployment..."

# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn[standard] python-multipart

# Start the backend server
echo "🌐 Starting Dragon Land Backend Server..."
cd /workspace
python -m uvicorn backend-api.app:app --host 0.0.0.0 --port 8000 --reload &

echo "✅ Server started on port 8000"
echo "🌍 Your server will be accessible via the Codespaces public URL"
echo "📱 Use this URL to update your APK for testing"