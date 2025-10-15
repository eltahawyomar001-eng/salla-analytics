#!/bin/bash

echo "========================================"
echo " Advanced Analysis for E-Commerce"
echo " Starting application..."
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run the application
echo
echo "========================================"
echo " Starting Streamlit..."
echo " App will open in your browser"
echo " Press Ctrl+C to stop"
echo "========================================"
echo

streamlit run app/main.py

# Deactivate on exit
deactivate
