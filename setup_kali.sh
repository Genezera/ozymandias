#!/bin/bash

# Output colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Tor OSINT Crawler setup for Kali Linux ===${NC}"

# 1. Install system packages
echo -e "\n${YELLOW}[*] Updating package list and installing Tor/Python venv...${NC}"
sudo apt update
sudo apt install -y tor python3-pip python3-venv

# 2. Start Tor service
echo -e "\n${YELLOW}[*] Starting Tor service...${NC}"
sudo service tor start

# Check if it started
if systemctl is-active --quiet tor; then
    echo -e "${GREEN}[OK] Tor service is running.${NC}"
else
    echo -e "${RED}[ERROR] Failed to start Tor. Try 'sudo service tor start' manually.${NC}"
fi

# 3. Set up Python virtual environment
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}[*] Creating virtual environment (venv)...${NC}"
    python3 -m venv venv
else
    echo -e "\n${YELLOW}[*] Virtual environment already exists.${NC}"
fi

# 4. Install dependencies
echo -e "\n${YELLOW}[*] Installing Python libraries...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Done
echo -e "\n${GREEN}=== Setup complete! ===${NC}"
echo -e "To run the project (recommended via dashboard):"
echo -e "1. Activate the venv: ${YELLOW}source venv/bin/activate${NC}"
echo -e "2. Start the dashboard: ${YELLOW}python -m streamlit run dashboard.py${NC}"
echo -e "\nOr run only the crawler from the terminal:"
echo -e "${YELLOW}python3 crawler.py${NC}"
