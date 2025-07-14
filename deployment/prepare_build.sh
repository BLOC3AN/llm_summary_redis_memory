#!/bin/bash

# Prepare environment for Docker build
echo "📦 Preparing environment for Docker build..."

# Check if source files exist in parent directory
if [ ! -d "../src" ]; then
    echo "❌ Source directory ../src not found!"
    exit 1
fi

if [ ! -f "../main.py" ]; then
    echo "❌ Main file ../main.py not found!"
    exit 1
fi

# Check .env file
if [ ! -f "../.env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚠️ No .env file found in parent directory"
        echo "💡 Please copy .env.example to ../.env and configure it"
        echo "   cp deployment/.env.example .env"
    else
        echo "❌ No .env.example found!"
        exit 1
    fi
else
    echo "✅ Found .env file in parent directory"
fi

echo "🎉 Environment check completed!"
echo "📁 Docker will build from parent directory context"
