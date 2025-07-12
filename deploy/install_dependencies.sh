#!/bin/bash
# Dependency installation script for Job Hunt Buddy

set -e  # Exit on any error
set -x  # Verbose output for debugging

# Configuration
PROJECT_DIR="/home/taylor/Development/jobhuntbot"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
PYTHON_BIN="/usr/bin/python3"  # Use `which python3` to confirm

echo "🔧 Installing/updating Job Hunt Buddy dependencies..."

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    cd "$PROJECT_DIR"
    $PYTHON_BIN -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
. "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install/upgrade requirements
echo "📦 Installing Python dependencies..."
pip install -r "$REQUIREMENTS_FILE"

# Install Playwright browsers (only if not already installed)
echo "🌐 Checking Playwright browsers..."
if ! $VENV_DIR/bin/playwright --version > /dev/null 2>&1; then
    echo "📥 Installing Playwright browsers..."
    $VENV_DIR/bin/playwright install chromium
else
    echo "✅ Playwright browsers already installed"
fi

echo "✅ Dependencies installation complete!" 