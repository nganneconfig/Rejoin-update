#!/bin/bash
cd
if [ -e "/data/data/com.termux/files/home/storage" ]; then
	rm -rf /data/data/com.termux/files/home/storage
fi
termux-setup-storage
yes | pkg update
. <(curl https://raw.githubusercontent.com/nganneconfig/rejoinshouko/refs/heads/main/termux-change-repo.sh)
yes | pkg upgrade
yes | pkg i python
yes | pkg i python-pip
pip install requests rich prettytable pytz
export CFLAGS="-Wno-error=implicit-function-declaration"
pip install psutil
curl -Ls "https://raw.githubusercontent.com/nganneconfig/Rejoin-update/refs/heads/main/rejoin_webhook.py" -o /sdcard/Download/rejoin_webhook.py
