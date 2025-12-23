#!/bin/bash
set -e

echo "=========================================="
echo "CMRIT Timetable Generation System Setup"
echo "DSA-Based Adaptive Scheduling"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p app/templates
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p data/generated_timetables
mkdir -p data/section_timetables

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To run the system:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Start web server: python run.py"
echo "  3. Open http://localhost:5000 in your browser"
echo ""
echo "Command line options:"
echo "  python run.py --help     # Show all options"
echo "  python run.py --test     # Run tests"
echo "  python run.py --cli      # CLI mode"
echo ""
echo "To start using the system:"
echo "1. Activate the environment:   source venv/bin/activate"
echo "2. Run the system:            python main.py"