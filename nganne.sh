#!/bin/bash
cd

# Setup storage
if [ -e "/data/data/com.termux/files/home/storage" ]; then
    rm -rf /data/data/com.termux/files/home/storage
fi
termux-setup-storage

# Update & change repo
yes | pkg update
. <(curl -fsSL https://raw.githubusercontent.com/nganneconfig/rejoinshouko/refs/heads/main/termux-change-repo.sh)
yes | pkg upgrade

# Install base packages
yes | pkg install python -y
yes | pkg install python-pip -y
yes | pkg install git -y
yes | pkg install curl -y

# Python dependencies
pip install --upgrade pip
pip install requests rich prettytable pytz psutil aiohttp pyfiglet

# Wake lock để giữ cho Termux không bị sleep
termux-wake-lock

# Tải tool về thư mục chính
curl -Ls "https://raw.githubusercontent.com/nganneconfig/Rejoin-update/refs/heads/main/rejoin_webhook.py" -o ~/rejoin_webhook.py
