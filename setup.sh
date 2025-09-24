#!/bin/bash
# Setup script for Real Estate Scraper

echo "Real Estate Scraper Setup"
echo "========================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

if [ $? -eq 0 ]; then
    echo "✅ Playwright browsers installed successfully"
else
    echo "⚠️  Warning: Failed to install Playwright browsers"
    echo "   This might be due to disk space issues."
    echo "   Try freeing up space and run: playwright install chromium"
fi

# Run system tests
echo "Running system tests..."
python3 test_scraper.py

if [ $? -eq 0 ]; then
    echo "✅ All system tests passed!"
else
    echo "❌ Some system tests failed"
    exit 1
fi

# Create data directories
echo "Creating data directories..."
mkdir -p data/{properties,images,logs}
echo "✅ Data directories created"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Usage examples:"
echo "  Full scrape (first run):     python3 main.py full"
echo "  Incremental sync:           python3 main.py sync"
echo "  Periodic sync (24h):        python3 main.py periodic"
echo "  Check status:               python3 main.py status"
echo ""
echo "⚠️  Note: The scraper includes anti-bot protection measures."
echo "   If you encounter rate limiting, the scraper will automatically"
echo "   implement delays and retry logic."