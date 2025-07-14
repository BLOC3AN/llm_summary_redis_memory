#!/bin/bash

# Prepare files for Docker build
echo "📦 Preparing files for Docker build..."

# Copy source code
cp -r ../src ./src
echo "✅ Copied src directory"

# Copy main files
cp ../main.py ./main.py
cp ../test_auto_summary.py ./test_auto_summary.py
cp ../demo_auto_summary.py ./demo_auto_summary.py
echo "✅ Copied Python files"

# Copy .env if it doesn't exist
if [ ! -f .env ]; then
    if [ -f ../.env ]; then
        cp ../.env ./.env
        echo "✅ Copied .env file"
    else
        echo "⚠️ No .env file found, using .env.example"
    fi
fi

echo "🎉 Build preparation completed!"
