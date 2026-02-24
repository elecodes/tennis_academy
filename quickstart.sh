#!/bin/bash

echo "=========================================="
echo "SF TENNIS KIDS Club - Quick Start Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "Step 1: Creating virtual environment..."
python3 -m venv venv

echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo "Step 3: Installing dependencies..."
pip install -r backend/requirements.txt

echo "Step 4: Initializing database..."
python3 -c "import sys; sys.path.insert(0, 'backend'); from app import init_db; init_db(); print('Database initialized!')"

echo ""
echo "Step 5: Would you like to add demo data? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python3 backend/demo_data.py
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. Set your email credentials:"
echo "     export SENDER_EMAIL=your-email@gmail.com"
echo "     export SENDER_PASSWORD=your-app-password"
echo ""
echo "  2. Run the app:"
echo "     python3 backend/app.py"
echo ""
echo "  3. Open browser and go to:"
echo "     http://localhost:5000"
echo ""
echo "  4. First time setup:"
echo "     Visit http://localhost:5000/setup to create admin account"
echo ""
echo "=========================================="
