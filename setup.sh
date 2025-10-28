#!/bin/bash
set -e

echo "=== Setting up Adaptive Timetable System ==="

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To start using the system:"
echo "1. Activate the environment:   source venv/bin/activate"
echo "2. Run the system:            python main.py"