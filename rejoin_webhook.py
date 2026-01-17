#!/usr/bin/env python3
import subprocess
import asyncio
import aiohttp
import json
import os
import sys
import time
from pathlib import Path
import re
from typing import Dict, Optional, List, Tuple
import platform
import psutil
from datetime import datetime
import shutil
import random
import requests
import traceback
import threading

def ensure_packages():
    required_packages = ["aiohttp", "psutil", "rich", "pyfiglet"]
    
    for pkg in required_packages:
        try:
            __import__(pkg)
        except ImportError:
            print(f"Đang cài package thiếu: {pkg}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Lỗi khi cài {pkg}: {e}")
                sys.exit(1)

ensure_packages()

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
import pyfiglet

console = Console()
CONFIG_PATH = Path(__file__).parent / "multi_configs.json"
WEBHOOK_CONFIG_PATH = Path(__file__).parent / "webhook_config.json"
def wait_back_menu():
    prompt_text = ("\nPress Enter to back to menu...", [220, 228, 229])
    input(prompt_text)
# DANH SÁCH PACKAGE BỔ SUNG TỪ ẢNH
ARYA_PACKAGES = [
    "com.arya.clienv",
    "com.arya.clienw", 
    "com.arya.clienx",
    "com.arya.clieny",
    "com.arya.clienz"
]

class AndroidIDManager:
    def __init__(self):
        self.auto_android_id_enabled = False
        self.auto_android_id_thread = None
        self.auto_android_id_value = None

    def set_android_id(self, android_id):
        try:
            subprocess.run(["settings", "put", "secure", "android_id", android_id], check=True)
            print(f"\033[1;32m[ Tool ] - Android ID set to: {android_id}\033[0m")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\033[1;31m[ Tool ] - Failed to set Android ID: {e}\033[0m")
            return False
        except Exception as e:
            print(f"\033[1;31m[ Tool ] - Error setting Android ID: {e}\033[0m")
            return False

    def auto_change_android_id(self):
        while self.auto_android_id_enabled:
            if self.auto_android_id_value:
                success = self.set_android_id(self.auto_android_id_value)
                if not success:
                    print("\033[1;33m[ Tool ] - Retrying Android ID change...\033[0m")
            time.sleep(2)

    def start_auto_android_id(self):
        if self.auto_android_id_enabled:
            print("\033[1;33m[ Tool ] - Auto Android ID change is already running!\033[0m")
            return False
        
        android_id = input("\033[1;93m[ Tool ] - Enter Android ID to continuously set: \033[0m").strip()
        
        if not android_id:
            print("\033[1;31m[ Tool ] - Android ID cannot be empty.\033[0m")
            return False
        
        if len(android_id) < 16:
            print("\033[1;33m[ Tool ] - Warning: Android ID seems too short. Continue? (y/n): \033[0m", end="")
            confirm = input().strip().lower()
            if confirm != 'y':
                return False
        
        self.auto_android_id_value = android_id
        self.auto_android_id_enabled = True
        
        if self.auto_android_id_thread is None or not self.auto_android_id_thread.is_alive():
            self.auto_android_id_thread = threading.Thread(target=self.auto_change_android_id, daemon=True)
            self.auto_android_id_thread.start()
        
        print(f"\033[1;32m[ Tool ] - Auto Android ID change enabled with ID: {android_id}\033[0m")
        print(f"\033[1;32m[ Tool ] - Android ID will be set every 2 seconds\033[0m")
        return True

    def stop_auto_android_id(self):
        if not self.auto_android_id_enabled:
            print("\033[1;33m[ Tool ] - Auto Android ID change is not running.\033[0m")
            return False
        
        self.auto_android_id_enabled = False
        print("\033[1;31m[ Tool ] - Auto Android ID change disabled.\033[0m")
        return True

    def toggle_auto_android_id(self):
        if not self.auto_android_id_enabled:
            return self.start_auto_android_id()
        else:
            return self.stop_auto_android_id()

    def get_auto_android_id_status(self):
        status = {
            "enabled": self.auto_android_id_enabled,
            "android_id": self.auto_android_id_value if self.auto_android_id_value else "Not set",
            "thread_alive": self.auto_android_id_thread.is_alive() if self.auto_android_id_thread else False
        }
        
        return status

    def get_current_android_id(self):
        try:
            result = subprocess.run(
                ["settings", "get", "secure", "android_id"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            current_id = result.stdout.strip()
            print(f"\033[1;36m[ Tool ] - Current Android ID: {current_id}\033[0m")
            return current_id
        except subprocess.CalledProcessError as e:
            print(f"\033[1;31m[ Tool ] - Failed to get current Android ID: {e}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m[ Tool ] - Error getting Android ID: {e}\033[0m")
            return None

    def android_id_menu(self):
        while True:
            print("\n" + "="*50)
            print("\033[1;34m[ ANDROID ID MANAGER ]\033[0m")
            print("="*50)
            
            status = self.get_auto_android_id_status()
            status_text = "\033[1;32mEnabled\033[0m" if status["enabled"] else "\033[1;31mDisabled\033[0m"
            
            print(f"Status: {status_text}")
            print(f"Target ID: {status['android_id']}")
            print(f"Thread Status: {'Running' if status['thread_alive'] else 'Stopped'}")
            
            print("\nOptions:")
            print("1. Toggle Auto Android ID Change")
            print("2. Set New Android ID")
            print("3. Get Current Android ID")
            print("4. Set Android ID Once")
            print("5. Exit to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "1":
                self.toggle_auto_android_id()
            elif choice == "2":
                if self.auto_android_id_enabled:
                    print("\033[1;33m[ Tool ] - Please stop auto mode first.\033[0m")
                else:
                    self.start_auto_android_id()
            elif choice == "3":
                self.get_current_android_id()
            elif choice == "4":
                android_id = input("Enter Android ID to set once: ").strip()
                if android_id:
                    self.set_android_id(android_id)
            elif choice == "5":
                if self.auto_android_id_enabled:
                    self.stop_auto_android_id()
                break
            else:
                print("\033[1;31m[ Tool ] - Invalid choice!\033[0m")
            
            input("\nPress Enter to continue...")

class WebhookManager:
    def __init__(self):
        self.webhook_url = None
        self.device_name = None
        self.interval = None
        self.enabled = False
        self.last_sent_time = 0
        self.load_config()

    def load_config(self):
        try:
            if WEBHOOK_CONFIG_PATH.exists():
                with open(WEBHOOK_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.webhook_url = config.get('webhook_url')
                    self.device_name = config.get('device_name', 'Unknown Device')
                    self.interval = config.get('interval', 60)
                    self.enabled = config.get('enabled', False) and self.webhook_url
        except Exception as e:
            print(f"❌ Lỗi load webhook config: {e}")

    def save_config(self):
        try:
            config = {
                'webhook_url': self.webhook_url,
                'device_name': self.device_name,
                'interval': self.interval,
                'enabled': self.enabled
            }
            with open(WEBHOOK_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Lỗi save webhook config: {e}")

    def setup_webhook(self):
        try:
            print("\n🔧 CẤU HÌNH DISCORD WEBHOOK")
            print("=" * 40)
            
            webhook_url = input("Nhập Discord Webhook URL: ").strip()
            if not webhook_url:
                print("❌ Webhook URL không được để trống!")
                return
            
            device_name = input("Nhập tên thiết bị: ").strip() or "Multi Dawn Device"
            interval = input("Nhập interval (phút, mặc định 60): ").strip()
            interval = int(interval) if interval.isdigit() else 60
            
            self.webhook_url = webhook_url
            self.device_name = device_name
            self.interval = interval
            self.enabled = True
            
            self.save_config()
            print("✅ Đã cấu hình webhook thành công!")
            
        except Exception as e:
            print(f"❌ Lỗi cấu hình webhook: {e}")

    def capture_screenshot(self):
        try:
            screenshot_path = "/data/data/com.termux/files/home/screenshot.png"
            commands = [
                f"screencap -p {screenshot_path}",
                f"su -c screencap -p {screenshot_path}",
                f"/system/bin/screencap -p {screenshot_path}"
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0 and os.path.exists(screenshot_path):
                        return screenshot_path
                except:
                    continue
            
            print("❌ Không thể chụp màn hình")
            return None
        except Exception as e:
            print(f"❌ Lỗi chụp màn hình: {e}")
            return None

    def get_system_info(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info = {
                "cpu_usage": f"{cpu_usage:.1f}%",
                "memory_used": f"{memory.used / (1024**3):.2f}GB",
                "memory_total": f"{memory.total / (1024**3):.2f}GB",
                "memory_percent": f"{memory.percent:.1f}%",
                "disk_used": f"{disk.used / (1024**3):.2f}GB",
                "disk_total": f"{disk.total / (1024**3):.2f}GB",
                "disk_percent": f"{disk.percent:.1f}%",
                "uptime": self.get_uptime(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return system_info
        except Exception as e:
            print(f"❌ Lỗi lấy system info: {e}")
            return None

    def get_uptime(self):
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
            
            days = int(uptime_seconds // (24 * 3600))
            hours = int((uptime_seconds % (24 * 3600)) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"

    def send_webhook(self, instances: List[Dict] = None):
        if not self.enabled or not self.webhook_url:
            return False

        try:
            current_time = time.time()
            if current_time - self.last_sent_time < self.interval * 60:
                return False

            print("📊 Đang gửi webhook...")
            
            screenshot_path = self.capture_screenshot()
            
            system_info = self.get_system_info()
            if not system_info:
                return False

            instances_info = ""
            if instances:
                for i, instance in enumerate(instances, 1):
                    package_name = instance.get('packageName', 'Unknown')
                    status = instance.get('status', 'Unknown')
                    username = instance.get('config', {}).get('username', 'Unknown')
                    
                    masked_username = username[:3] + "***" if len(username) > 3 else username
                    
                    instances_info += f"{i}. {package_name} ({masked_username}) - {status}\n"
            else:
                instances_info = "Không có instances đang chạy"

            random_color = random.randint(0, 16777215)
            
            embed = {
                "color": random_color,
                "title": "📈 Multi Rejoin Ngan - System Status",
                "description": f"Real-time report for **{self.device_name}**",
                "fields": [
                    {
                        "name": "💻 CPU Usage",
                        "value": f"```{system_info['cpu_usage']}```",
                        "inline": True
                    },
                    {
                        "name": "🧠 Memory Usage",
                        "value": f"```{system_info['memory_used']} / {system_info['memory_total']} ({system_info['memory_percent']})```",
                        "inline": True
                    },
                    {
                        "name": "💾 Disk Usage",
                        "value": f"```{system_info['disk_used']} / {system_info['disk_total']} ({system_info['disk_percent']})```",
                        "inline": True
                    },
                    {
                        "name": "⏰ Uptime",
                        "value": f"```{system_info['uptime']}```",
                        "inline": True
                    },
                    {
                        "name": "🕐 Last Update",
                        "value": f"```{system_info['timestamp']}```",
                        "inline": True
                    },
                    {
                        "name": "🎮 Running Instances",
                        "value": f"```{instances_info}```",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Ngan Rejoin Tool | Made with ❤️",
                    "icon_url": "https://cdn.discordapp.com/attachments/1269331861902196902/1422144505485721653/1.png?ex=68db9ac8&is=68da4948&hm=a7ed4d0a5740ff876e12b22f94f3e14df81d5396fb504b52251f1382e65d1211&"
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "author": {
                    "name": "Rejoin By Ngan",
                    "icon_url": "https://cdn.discordapp.com/attachments/1269331861902196902/1422144505485721653/1.png?ex=68db9ac8&is=68da4948&hm=a7ed4d0a5740ff876e12b22f94f3e14df81d5396fb504b52251f1382e65d1211&"
                }
            }

            payload = {
                "embeds": [embed],
                "username": "Rejoin By Ngan🔥",
                "avatar_url": "https://cdn.discordapp.com/attachments/1269331861902196902/1422144505485721653/1.png?ex=68db9ac8&is=68da4948&hm=a7ed4d0a5740ff876e12b22f94f3e14df81d5396fb504b52251f1382e65d1211&"
            }

            files = {}
            if screenshot_path and os.path.exists(screenshot_path):
                with open(screenshot_path, 'rb') as f:
                    files['file'] = ('screenshot.png', f, 'image/png')
                    response = requests.post(
                        self.webhook_url,
                        data={"payload_json": json.dumps(payload)},
                        files=files
                    )
            else:
                response = requests.post(
                    self.webhook_url,
                    json=payload
                )

            if response.status_code in [200, 204]:
                print("✅ Đã gửi webhook thành công!")
                self.last_sent_time = current_time
                
                if screenshot_path and os.path.exists(screenshot_path):
                    try:
                        os.remove(screenshot_path)
                    except:
                        pass
                return True
            else:
                print(f"❌ Lỗi gửi webhook: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Lỗi gửi webhook: {e}")
            return False
def detect_roblox_packages_by_keywords():
    keywords = [
        # ===== ORIGINAL (GIỮ NGUYÊN) =====
        "roblox", "bduy", "mangcut", "concacug", "louis", "zamdepzai",
        "ugpornkiki", "zam.nagy", "fynix.clone", "arya",

        # ===== ROBLOX CLONE / MOD =====
        "robloxmod", "robloxclone", "rbxclone", "rbxmod",
        "robloxmulti", "multiroblox", "robloxdual", "roblox2",
        "robloxplus", "robloxx", "robloxalt",

        # ===== EXECUTOR / TOOL NAME =====
        "delta", "codex", "fluxus", "arceus", "hydrogen",
        "krnl", "synapse", "electron", "evon", "scriptware",

        # ===== PRIVATE / CUSTOM BUILD =====
        "private", "custom", "build", "patched", "modified",
        "inject", "loader", "bypass", "stealth",

        # ===== USER / DEV TAG =====
        "dev", "owner", "admin", "test", "beta",
        "release", "pro", "vip", "premium",

        # ===== ANDROID / MOBILE =====
        "android", "mobile", "apk", "client",
        "arm", "arm64", "v7a", "v8a",

        # ===== MULTI / FARM =====
        "multi", "clone", "farm", "auto",
        "bot", "afk", "grind",

        # ===== RANDOM TAGS =====
        "shadow", "ghost", "night", "dark",
        "zero", "neo", "alpha", "omega",
        "x1", "x2", "x3", "promax"
    ]

    pkgs = []
    result = os.popen("pm list packages").read().splitlines()

    for line in result:
        pkg = line.replace("package:", "").strip().lower()
        if any(k in pkg for k in keywords):
            pkgs.append(pkg)

    return list(dict.fromkeys(pkgs))  # remove duplicate


def logout_current_account(pkg: str):
    """
    Logout account hiện tại bằng cách xóa cookie .ROBLOSECURITY
    KHÔNG clear toàn app
    Yêu cầu: root / emulator
    """
    try:
        cookie_db = f"/data/data/{pkg}/app_webview/Default/Cookies"

        if not os.path.exists(cookie_db):
            msg(f"Cookie DB not found for {pkg}", "err")
            return

        conn = sqlite3.connect(cookie_db)
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM cookies
            WHERE host_key LIKE '%roblox.com%'
        """)

        conn.commit()
        conn.close()

        # kill app để cookie áp dụng
        os.system(f"am force-stop {pkg}")

        msg(f"Logged out  account : {pkg}", "ok")

    except Exception as e:
        msg(f"Logout account failed {pkg}: {e}", "err")
        
def logacc():
            try:
                clear()
                print("\033[96m==== Logout Roblox Accounts ====\033[0m")
                print("  [1] Logout CURRENT account (ALL Packages)")
                print("  [2] Select Package Logout (CURRENT account only)")

                sel = input("\n\033[92mSelect option: \033[0m").strip()

                # ===== OPTION 1: LOGOUT CURRENT ACCOUNT - ALL PACKAGES =====
                if sel == "1":
                    confirm = input(
                        "\033[35;1mLogout CURRENT account of ALL Roblox packages? (y/N): \033[0m"
                    ).strip().lower()

                    if confirm != "y":
                        msg("Cancelled.", "warn")
                        wait_back_menu()
                        return

                    pkgs = detect_roblox_packages_by_keywords()

                    if not pkgs:
                        msg("No Roblox packages detected.", "err")
                        wait_back_menu()
                        return 

                    for pkg in pkgs:
                        logout_current_account(pkg)

                    msg("Logged out CURRENT account on all detected packages.", "ok")
                    wait_back_menu()
                    return 

                # ===== OPTION 2: SELECT PACKAGE =====
                elif sel == "2":
                    pkgs = detect_roblox_packages_by_keywords()

                    if not pkgs:
                        msg("No Roblox packages detected.", "err")
                        wait_back_menu()
                        return 

                    print("\n\033[96mDetected Packages:\033[0m")
                    for i, pkg in enumerate(pkgs, 1):
                        print(f"  [{i}] {pkg}")

                    selected = []

                    while True:
                        s = input("\nSelect Package Logout (0 = stop): ").strip()

                        if not s.isdigit():
                            return 

                        num = int(s)

                        if num == 0:
                            break

                        if 1 <= num <= len(pkgs):
                            pkg = pkgs[num - 1]
                            if pkg not in selected:
                                selected.append(pkg)
                                print(f"Added: {pkg}")

                    if not selected:
                        msg("No package selected.", "warn")
                        wait_back_menu()
                        return 

                    confirm = input(
                        "\033[35;1mLogout CURRENT account on selected packages? (y/N): \033[0m"
                    ).strip().lower()

                    if confirm != "y":
                        msg("Cancelled.", "warn")
                        wait_back_menu()
                        return 

                    for pkg in selected:
                        logout_current_account(pkg)

                    msg("Logged out CURRENT account on selected packages.", "ok")
                    wait_back_menu()
                    return 

                else:
                    msg("Invalid option.", "err")
                    wait_back_menu()
                    return 

            except Exception as e:
                msg(f"Error while logout menu: {e}", "err")
                wait_back_menu()
# --------------- Cookie ----------

def download_file(url, destination, binary=True, timeout=15):

    try:

        r = requests.get(url, stream=True, timeout=timeout)

        if r.status_code == 200:

            mode = 'wb' if binary else 'w'

            with open(destination, mode) as f:

                if binary:

                    shutil.copyfileobj(r.raw, f)

                else:

                    f.write(r.text)

            return destination

        else:

            print(f"\033[35;1m[cookie] download failed {url} -> status {r.status_code}\033[0m")

            return None

    except Exception as e:

        print(f"\033[35;1m[cookie] download_file error: {e}\033[0m")

        return None





class CookieInjector:

    @staticmethod

    def get_cookie():

        """

        Lấy 1 cookie hợp lệ từ cookie.txt (dạng bắt đầu _|WARNING: ...)

        Di chuyển bản gốc sang BduyOnTop/Shoụko.dev - Data/cookie.txt

        Trả về cookie string hoặc False nếu không có.

        """

        try:

            current_dir = os.getcwd()

            cookie_txt_path = os.path.join(current_dir, "cookie.txt")

            new_dir_path = os.path.join(current_dir, "BduyOnTop", "bduy - Data")

            new_cookie_path = os.path.join(new_dir_path, "cookie.txt")



            os.makedirs(new_dir_path, exist_ok=True)



            if not os.path.exists(cookie_txt_path):

                print("[cookie] cookie.txt not found")

                return False



            cookies, org = [], []

            with open(cookie_txt_path, "r", encoding="utf-8", errors="ignore") as file:

                for line in file:

                    line = line.rstrip("\n")

                    parts = line.split(":")

                    ck = ":".join(parts[2:]) if len(parts) == 4 else line

                    if ck.startswith("_|WARNING"):

                        org.append(line)

                        cookies.append(ck)



            if not cookies:

                print("\033[35;1m[cookie] no valid cookies in cookie.txt\033[0m")

                return False



            cookie = cookies.pop(0)

            original_line = org.pop(0)



            with open(new_cookie_path, "a", encoding="utf-8") as newf:

                newf.write(original_line + "\n")



            with open(cookie_txt_path, "w", encoding="utf-8") as f:

                f.write("\n".join(org))



            return cookie

        except Exception as e:

            print(f"\033[35;1m[cookie] get_cookie error: {e}\033[0m")

            return False



    @staticmethod

    def verify_cookie(cookie_value):

        try:

            headers = {

                'Cookie': f'.ROBLOSECURITY={cookie_value}',

                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile)',

                'Referer': 'https://www.roblox.com/',

                'Origin': 'https://www.roblox.com'

            }

            time.sleep(1)

            r = requests.get('https://users.roblox.com/v1/users/authenticated', headers=headers, timeout=10)

            if r.status_code == 200:

                return r.json().get("id", False)

            return False

        except Exception as e:

            print(f"\033[35;1m[cookie] verify_cookie error: {e}\033[0m")

            return False



    @staticmethod

    def replace_cookie_value_in_db(db_path, new_cookie_value):

        try:

            conn = sqlite3.connect(db_path)

            cursor = conn.cursor()

            # cập nhật cookie trong Chromium Cookie DB

            now100ns = int(time.time() + 11644473600) * 1000000

            exp100ns = int(time.time() + 11644473600 + 31536000) * 1000000

            cursor.execute(

                "UPDATE cookies SET value = ?, last_access_utc = ?, expires_utc = ? "

                "WHERE host_key = '.roblox.com' AND name = '.ROBLOSECURITY'",

                (new_cookie_value, now100ns, exp100ns)

            )

            conn.commit()

            conn.close()

            print("\033[35;1m[cookie] cookie value replaced in DB\033[0m")

        except Exception as e:

            print(f"\033[35;1m[cookie] replace_cookie_value_in_db error: {e}\033[0m")



    @staticmethod

    def inject_cookies_and_appstorage():

        """

        Tải Cookies DB + appStorage.json, copy vào từng package,

        thay giá trị .ROBLOSECURITY trong DB. YÊU CẦU quyền ghi /data/data (root/emulator).

        """

        # dừng app (basic)

        try:

            for pkg in detect_roblox_packages_by_keywords():

                os.system(f"pkill -f {pkg}")

        except Exception:

            pass



        db_url = "https://raw.githubusercontent.com/nghvit/module/refs/heads/main/import/Cookies"

        appstorage_url = "https://raw.githubusercontent.com/nghvit/module/refs/heads/main/import/appStorage.json"



        downloaded_db = download_file(db_url, "Cookies.db", binary=True)

        downloaded_appstorage = download_file(appstorage_url, "appStorage.json", binary=False)

        if not downloaded_db or not downloaded_appstorage:

            print("\033[35;1m[cookie] failed to download Cookies/appStorage.json\033[0m")

            return



        packages = detect_roblox_packages_by_keywords()

        if not packages:

            print("\033[35;1m[cookie] no packages detected\033[0m")

            return



        for pkg in packages:

            cookie = CookieInjector.get_cookie()

            if not cookie:

                print(f"\033[35;1m[cookie] no cookie left for {pkg}, skip\033[0m")

                continue



            uid = CookieInjector.verify_cookie(cookie)

            if not uid:

                print(f"\033[35;1m[cookie] invalid cookie for {pkg}, skip\033[0m")

                continue



            print(f"\033[35;1m[cookie] injecting -> {pkg}, uid={uid}\033[0m")



            dest_db_dir = f"/data/data/{pkg}/app_webview/Default/"

            dest_appstorage_dir = f"/data/data/{pkg}/files/appData/LocalStorage/"



            try:

                os.makedirs(dest_db_dir, exist_ok=True)

                os.makedirs(dest_appstorage_dir, exist_ok=True)



                dest_db_path = os.path.join(dest_db_dir, "Cookies")

                dest_appstorage_path = os.path.join(dest_appstorage_dir, "appStorage.json")



                shutil.copyfile(downloaded_db, dest_db_path)

                shutil.copyfile(downloaded_appstorage, dest_appstorage_path)



                CookieInjector.replace_cookie_value_in_db(dest_db_path, cookie)

                print(f"\033[35;1m[cookie] injected cookie -> {pkg} OK\033[0m")

            except Exception as e:

                print(f"\033[35;1m[cookie] inject failed for {pkg}: {e}\033[0m")



        print("\033[35;1m[cookie] injection completed\033[0m")

# <<< PATCH END                
class Utils:
    @staticmethod
    def ensure_root():
        try:
            if os.getuid() != 0:
                print("Cần quyền root, chuyển qua su...")
                python_path = "/data/data/com.termux/files/usr/bin/python"
                subprocess.run(f"su -c '{python_path} {__file__}'", shell=True, check=True)
                sys.exit(0)
        except AttributeError:
            pass
        except subprocess.CalledProcessError as e:
            print(f"Không thể chạy với quyền root: {e}")
            sys.exit(1)

    @staticmethod
    def enable_wake_lock():
        try:
            subprocess.run("termux-wake-lock", shell=True, check=False)
            print("Wake lock bật ⚡")
        except:
            print("Không bật được wake lock 😅")

    @staticmethod
    async def kill_app(package_name: str):
        try:
            print(f"💀 [{package_name}] Đang kill app...")
            subprocess.run(f"am force-stop {package_name}", shell=True, check=False, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ [{package_name}] Đã kill thành công!")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"❌ [{package_name}] Lỗi khi kill app: {e}")

    @staticmethod
    async def launch(place_id: str, link_code: Optional[str], package_name: str):
        url = f"roblox://placeID={place_id}"
        if link_code:
            url += f"&linkCode={link_code}"
        
        print(f"🚀 [{package_name}] Đang mở: {url}")
        if link_code:
            print(f"✨ [{package_name}] Đã join bằng linkCode: {link_code}")

        if package_name in ["com.roblox.client", "com.roblox.client.vnggames"]:
            activity = "com.roblox.client.ActivityProtocolLaunch"
        else:
            activity = "com.roblox.client.ActivityProtocolLaunch"

        command = f'am start -n {package_name}/{activity} -a android.intent.action.VIEW -d "{url}" --activity-clear-top'
        
        try:
            subprocess.run(command, shell=True, check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ [{package_name}] Launch command executed!")
        except Exception as e:
            print(f"❌ [{package_name}] Launch failed: {e}")

    @staticmethod
    def ask(msg: str) -> str:
        return input(msg)

    @staticmethod
    def save_multi_configs(configs: Dict):
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(configs, f, indent=2, ensure_ascii=False)
            print(f"💾 Đã lưu multi configs tại {CONFIG_PATH}")
        except Exception as e:
            print(f"❌ Không thể lưu configs: {e}")

    @staticmethod
    def load_multi_configs() -> Dict:
        if not CONFIG_PATH.exists():
            return {}
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    @staticmethod
    def detect_all_roblox_packages() -> Dict:
        packages = {}
        
        try:
            # Tìm các package Roblox thông thường
            result = subprocess.run("pm list packages | grep -E 'com.roblox|com.arya.clien'", 
                                  shell=True, capture_output=True, text=True)
            lines = [line for line in result.stdout.split('\n') if line]
            
            for line in lines:
                match = re.search(r'package:(com\.[^\s]+)', line)
                if match:
                    package_name = match.group(1)
                    
                    # Xác định display name dựa trên package
                    if package_name == 'com.roblox.client':
                        display_name = 'Roblox Quốc tế 🌍'
                    elif package_name == 'com.roblox.client.vnggames':
                        display_name = 'Roblox VNG 🇻🇳'
                    elif package_name in ARYA_PACKAGES:
                        # Lấy ký tự cuối cùng từ package name (v, w, x, y, z)
                        version = package_name[-1].upper()
                        display_name = f'Arya Client {version} 🔥'
                    elif 'roblox' in package_name.lower():
                        display_name = f'Roblox Custom ({package_name}) 🎮'
                    elif 'arya' in package_name.lower():
                        display_name = f'Arya Client ({package_name}) ⚡'
                    else:
                        display_name = f'Unknown ({package_name}) ❓'
                    
                    packages[package_name] = {
                        'packageName': package_name,
                        'displayName': display_name
                    }
            
            # Thêm các package Arya nếu chưa được tìm thấy
            for arya_pkg in ARYA_PACKAGES:
                if arya_pkg not in packages:
                    version = arya_pkg[-1].upper()
                    packages[arya_pkg] = {
                        'packageName': arya_pkg,
                        'displayName': f'Arya Client {version} 🔥'
                    }
                    
        except Exception as e:
            print(f"❌ Lỗi khi quét packages: {e}")

        return packages

    @staticmethod
    def get_roblox_cookie(package_name: str) -> Optional[str]:
        print(f"🍪 [{package_name}] Đang lấy cookie ROBLOSECURITY...")
        
        try:
            cmd = f"cat /data/data/{package_name}/app_webview/Default/Cookies | strings | grep ROBLOSECURITY"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            raw = result.stdout
        except:
            try:
                cmd = f"su -c sh -c 'cat /data/data/{package_name}/app_webview/Default/Cookies | strings | grep ROBLOSECURITY'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                raw = result.stdout
            except Exception:
                print(f"❌ [{package_name}] Không thể đọc cookie bằng cả 2 cách.")
                return None

        match = re.search(r'\.ROBLOSECURITY_([^\s/]+)', raw)
        if not match:
            print(f"❌ [{package_name}] Không tìm được cookie ROBLOSECURITY!")
            return None

        cookie_value = match.group(1).strip()
        if not cookie_value.startswith("_"):
            cookie_value = "_" + cookie_value
        
        return f".ROBLOSECURITY={cookie_value}"

class GameLauncher:
    @staticmethod
    async def handle_game_launch(should_launch: bool, place_id: str, link_code: Optional[str], 
                               package_name: str, rejoin_only: bool = False):
        if should_launch:
            print(f"🎯 [{package_name}] Starting launch process...")
            
            if not rejoin_only:
                await Utils.kill_app(package_name)
            else:
                print(f"⚠️ [{package_name}] RejoinOnly mode - không kill app")

            await Utils.launch(place_id, link_code, package_name)
            
            print(f"✅ [{package_name}] Launch process completed!")

class RobloxUser:
    def __init__(self, username: Optional[str] = None, user_id: Optional[int] = None, 
                 cookie: Optional[str] = None):
        self.username = username
        self.user_id = user_id
        self.cookie = cookie

    async def fetch_authenticated_user(self) -> Optional[int]:
        try:
            headers = {
                'Cookie': self.cookie,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Termux)',
                'Accept': 'application/json',
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get("https://users.roblox.com/v1/users/authenticated", 
                                     headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.username = data['name']
                        self.user_id = data['id']
                        print(f"✅ Lấy info thành công cho {self.username}!")
                        return self.user_id
                    else:
                        print(f"❌ HTTP Error: {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Lỗi xác thực người dùng: {e}")
            return None

    async def get_presence(self) -> Optional[Dict]:
        try:
            headers = {
                'Cookie': self.cookie,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Termux)',
                'Accept': 'application/json',
            }
            
            data = {'userIds': [self.user_id]}
            
            async with aiohttp.ClientSession() as session:
                async with session.post("https://presence.roproxy.com/v1/presence/users",
                                      json=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('userPresences', [{}])[0] if result.get('userPresences') else None
                    return None
        except:
            return None

class GameSelector:
    def __init__(self):
        self.GAMES = {
            "1": ["126884695634066", "Grow-a-Garden 🍒"],
            "2": ["2753915549", "Blox-Fruits 🍌"],
            "3": ["6284583030", "Pet-Simulator-X 🐾"],
            "4": ["126244816328678", "DIG ⛏️"],
            "5": ["116495829188952", "Dead-Rails-Alpha 🚂"],
            "6": ["8737602449", "PLS-DONATE 💰"],
            "0": ["custom", "Tùy chỉnh 🔍"],
        }

    async def choose_game(self) -> Dict:
        print("\n🎮 Chọn game:")
        for k, v in self.GAMES.items():
            print(f"{k}. {v[1]} ({v[0]})")

        ans = Utils.ask("Nhập số: ").strip()

        if ans == "0":
            sub = Utils.ask("0.1 ID thủ công | 0.2 Link private redirect: ").strip()
            if sub == "1":
                pid = Utils.ask("Nhập Place ID: ").strip()
                return {"placeId": pid, "name": "Tùy chỉnh ⚙️", "linkCode": None}
            elif sub == "2":
                print("\n📎 Dán link redirect sau khi vào private server.")
                while True:
                    link = Utils.ask("\nDán link redirect đã chuyển hướng: ")
                    match = re.search(r'/games/(\d+)[^?]*\?[^=]*=([\w-]+)', link)
                    if not match:
                        print("❌ Link không hợp lệ!")
                        continue
                    return {
                        "placeId": match.group(1),
                        "name": "Private Server 🔒",
                        "linkCode": match.group(2),
                    }
            raise ValueError("❌ Không hợp lệ!")

        if ans in self.GAMES:
            return {
                "placeId": self.GAMES[ans][0],
                "name": self.GAMES[ans][1],
                "linkCode": None,
            }

        raise ValueError("❌ Không hợp lệ!")

class StatusHandler:
    def __init__(self):
        self.has_launched = False
        self.joined_at = 0

    def analyze_presence(self, presence: Optional[Dict], target_root_place_id: str) -> Dict:
        now = int(time.time() * 1000)

        if not presence or presence.get('userPresenceType') is None:
            return {
                'status': "Không rõ ❓",
                'info': "Không lấy được trạng thái hoặc thiếu rootPlaceId",
                'shouldLaunch': True,
                'rejoinOnly': False
            }

        if presence.get('userPresenceType') in [0, 1]:
            return {
                'status': "Offline 💤",
                'info': "User offline! Tiến hành rejoin! 🚀",
                'shouldLaunch': True,
                'rejoinOnly': False
            }

        if presence.get('userPresenceType') != 2:
            return {
                'status': "Không online 🤔",
                'info': "User không trong game. Đã mở lại game! 🎮",
                'shouldLaunch': True,
                'rejoinOnly': False
            }

        root_place_id = presence.get('rootPlaceId')
        if not root_place_id or str(root_place_id) != str(target_root_place_id):
            return {
                'status': "Sai map rồi 🗺️",
                'info': f"User đang trong game nhưng sai rootPlaceId ({root_place_id}). Đã rejoin đúng map! 🎯",
                'shouldLaunch': True,
                'rejoinOnly': True
            }

        return {
            'status': "Online ✅",
            'info': "đúng game 🎮",
            'shouldLaunch': False,
            'rejoinOnly': False
        }

    def update_join_status(self, should_launch: bool):
        if should_launch:
            self.joined_at = int(time.time() * 1000)
            self.has_launched = True

class UIRenderer:
    @staticmethod
    def get_system_stats() -> Dict:
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024 ** 3)
            used_gb = (memory.total - memory.available) / (1024 ** 3)

            return {
                'cpuUsage': f"{cpu_usage:.1f}",
                'ramUsage': f"{used_gb:.2f}GB/{total_gb:.2f}GB"
            }
        except Exception as e:
            console.print("[red bold]Lỗi khi lấy system stats:[/red bold]", e)
            return {
                'cpuUsage': "N/A",
                'ramUsage': "N/A"
            }

    @staticmethod
    def render_title() -> str:
        fallback_title = """
╔═══════════════════════════════════════════════════════╗
║    🛒 𝗦𝗧𝗢𝗥𝗘𝟭𝗦.𝗖𝗢𝗠 • Premium E-Commerce Platform    ║
║         Your Trusted Shopping Destination            ║
║           Cửa Hàng Account Blox Fruit Uy tín S1 🇻🇳  ║
║           © 2024 STORE1S.COM • All Rights Reserved   ║
╚═══════════════════════════════════════════════════════╝"""
        try:
            try:
                title = pyfiglet.figlet_format("Arya rejoin", font="big")
            except Exception:
                console.print("[yellow]⚠️ Font 'big' lỗi, dùng font mặc định[/yellow]")
                title = pyfiglet.figlet_format("Store1st.com")
            
            with console.capture() as capture:
                console.print(title + "\n🚀 REJOIN TOOL BY NGÂN🚀", style="cyan")
                console.print("[bright_blue]🔗 Discord: https://discord.gg/qDBBG2RAQF[/bright_blue]")
                console.print("[magenta]🧩 Version: 2.0  | Free Termux[/magenta]\n")
            return capture.get()

        except Exception:
            console.print("[red bold]❌ Lỗi trong render_title():[/red bold]")
            traceback.print_exc()
            return fallback_title

    @staticmethod
    def format_countdown(seconds: int) -> str:
        return f"{seconds // 60}m {seconds % 60}s" if seconds >= 60 else f"{seconds}s"

    @staticmethod
    def render_multi_instance_table(instances: List[Dict]) -> str:
        try:
            stats = UIRenderer.get_system_stats()
            cpu_ram_line = f"💻 CPU: {stats['cpuUsage']}% | 🧠 RAM: {stats['ramUsage']} | 🔥 Instances: {len(instances)}"

            table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
            table.add_column("Package", style="dim", width=15)
            table.add_column("User", width=8)
            table.add_column("Status", width=12)
            table.add_column("Info", width=25)
            table.add_column("Time", width=8)
            table.add_column("Delay", width=6)

            for instance in instances:
                package_name = instance.get('packageName', '')
                if package_name == 'com.roblox.client':
                    package_display = 'Global 🌍'
                elif package_name == 'com.roblox.client.vnggames':
                    package_display = 'VNG 🇻🇳'
                elif package_name in ARYA_PACKAGES:
                    version = package_name[-1].upper()
                    package_display = f'Arya {version} 🔥'
                elif 'arya' in package_name.lower():
                    package_display = 'Arya ⚡'
                else:
                    package_display = package_name

                raw_username = instance.get('config', {}).get('username', 'Unknown')
                username = '*' * (len(raw_username) - 3) + raw_username[-3:] if len(raw_username) > 3 else raw_username

                delay_seconds = instance.get('countdownSeconds', 0)

                table.add_row(
                    package_display,
                    username,
                    instance.get('status', 'Unknown'),
                    instance.get('info', 'No info'),
                    datetime.now().strftime("%H:%M:%S"),
                    UIRenderer.format_countdown(delay_seconds)
                )

            with console.capture() as capture:
                console.print(cpu_ram_line)
                console.print(table)
            return capture.get()

        except Exception:
            console.print("[red bold]❌ Lỗi trong render_multi_instance_table():[/red bold]")
            traceback.print_exc()
            return "[Lỗi render table]"

    @staticmethod
    def display_configured_packages(configs: Dict) -> str:
        try:
            table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
            table.add_column("STT", width=5)
            table.add_column("Package", width=20)
            table.add_column("Username", width=15)
            table.add_column("Game", width=20)
            table.add_column("Delay", width=8)

            for index, (package_name, config) in enumerate(configs.items(), start=1):
                if package_name == 'com.roblox.client':
                    package_display = 'Global 🌍'
                elif package_name == 'com.roblox.client.vnggames':
                    package_display = 'VNG 🇻🇳'
                elif package_name in ARYA_PACKAGES:
                    version = package_name[-1].upper()
                    package_display = f'Arya {version} 🔥'
                elif 'arya' in package_name.lower():
                    package_display = 'Arya ⚡'
                else:
                    package_display = package_name

                username = config.get('username', 'Unknown')
                masked_username = '*' * (len(username) - 3) + username[-3:] if len(username) > 3 else username

                table.add_row(
                    str(index),
                    package_display,
                    masked_username,
                    config.get('gameName', 'Unknown'),
                    f"{config.get('delaySec', 0)}s"
                )

            with console.capture() as capture:
                console.print(table)
            return capture.get()

        except Exception:
            console.print("[red bold]❌ Lỗi trong display_configured_packages():[/red bold]")
            traceback.print_exc()
            return "[Lỗi render config table]"
def login_cookie():
                try:
                    print("\033[95m=== Cookie Injection Menu ===\033[0m")
                    print("\033[92m1. Enter cookies manually (multi-line, type 'end' to finish)\033[0m")
                    print("\033[96m2. Load cookies from cookie.txt file\033[0m")

                    method = input("\033[93mEnter choice (1/2): \033[0m").strip()
                    cookies = []

                    # ===== METHOD 1 : MANUAL INPUT =====
                    if method == "1":
                        print("\033[90mPaste cookies below (one per line). Type 'end' to finish.\033[0m")
                        while True:
                            line = input().strip()
                            if line.lower() == "end":
                                break
                            if line:
                                cookies.append(line)

                        if not cookies:
                            msg("No cookies were entered.", "err")
                            wait_back_menu()
                            return 

                        with open("cookie.txt", "w", encoding="utf-8") as f:
                            f.write("\n".join(cookies))
                        msg("Cookies saved successfully to cookie.txt", "ok")

                    # ===== METHOD 2 : LOAD FROM FILE =====
                    elif method == "2":
                        try:
                            with open("cookie.txt", "r", encoding="utf-8") as f:
                                cookies = [line.strip() for line in f if line.strip()]

                            if not cookies:
                                msg("cookie.txt is empty.", "err")
                                wait_back_menu()
                                return 

                            msg("Cookies loaded from cookie.txt", "ok")

                        except FileNotFoundError:
                            msg("cookie.txt not found. Please create it first.", "err")
                            wait_back_menu()
                            return 

                    else:
                        msg("Invalid input. Please select 1 or 2.", "err")
                        wait_back_menu()
                        return 

                    # ===== PACKAGE SELECTION =====
                    print("\n\033[94mInject cookies into specific Roblox packages?\033[0m")
                    print("\033[93m1. Yes, select packages\033[0m")
                    print("\033[93m2. No, inject using default method\033[0m")

                    pkg_choice = input("\033[93mEnter choice (1/2): \033[0m").strip()

                    # ===== DEFAULT INJECTION =====
                    if pkg_choice == "2":
                        try:
                            CookieInjector.inject_cookies_and_appstorage()
                            msg("Cookie injection completed (default mode)", "ok")
                        except Exception as e:
                            msg(f"Cookie injection failed: {e}", "err")
                        wait_back_menu()
                        return 

                    # ===== PACKAGE-SPECIFIC INJECTION =====
                    if pkg_choice == "1":
                        result = os.popen("pm list packages").read().splitlines()
                        keywords = [
                            "roblox", "bduy", "mangcut", "concacug",
                            "tencent", "ugpornkiki", "zam.nagy", "fynix.clone", "meow"
                        ]

                        pkgs = []
                        for line in result:
                            pkg = line.replace("package:", "").strip()
                            if any(kw in pkg.lower() for kw in keywords):
                                pkgs.append(pkg)

                        if not pkgs:
                            msg("No Roblox-related packages detected.", "err")
                            wait_back_menu()
                            return 

                        msg("Detected Roblox packages:", "ok")
                        for idx, pkg in enumerate(pkgs, 1):
                            print(f"[{idx}] {pkg}")

                        print("\n\033[93mSelect package numbers (space-separated, 0 = cancel): \033[0m")
                        sel = input().strip().split()

                        selected_pkgs = []
                        for s in sel:
                            if not s.isdigit():
                                return 
                            num = int(s)
                            if num == 0:
                                break
                            if 1 <= num <= len(pkgs):
                                selected_pkgs.append(pkgs[num - 1])

                        if not selected_pkgs:
                            msg("No packages selected. Operation cancelled.", "warn")
                            wait_back_menu()
                            return

                        # ===== MULTI THREAD INJECTION =====
                        def inject_worker(pkg):
                            try:
                                msg(f"Injecting cookies into {pkg} ...", "info")
                                try:
                                    CookieInjector.inject_cookies_and_appstorage(pkg)
                                except TypeError:
                                    try:
                                        CookieInjector.current_target_package = pkg
                                    except Exception:
                                        pass
                                    CookieInjector.inject_cookies_and_appstorage()
                                msg(f"Successfully injected into {pkg}", "ok")
                            except Exception as e:
                                msg(f"Injection failed for {pkg}: {e}", "err")

                        threads = []
                        # ===== SAFE SEQUENTIAL INJECTION (NO MIX PACKAGE) =====
                        for pkg in selected_pkgs:
                            try:
                                msg(f"Injecting cookies into {pkg} ...", "info")

                                try:
                                    CookieInjector.inject_cookies_and_appstorage(pkg)
                                except TypeError:
                                    # fallback nếu injector không support arg
                                    CookieInjector.current_target_package = pkg
                                    CookieInjector.inject_cookies_and_appstorage()

                                msg(f"Successfully injected into {pkg}", "ok")

                                # delay nhỏ để tránh race
                                time.sleep(0.5)

                            except Exception as e:
                                msg(f"Injection failed for {pkg}: {e}", "err")

                        msg("Cookie injection completed for selected packages.", "ok")
                        wait_back_menu()
                        return 

                    msg("Invalid package injection option.", "err")
                    wait_back_menu()

                except Exception as e:
                    msg(f"Cookie injection error: {e}", "err")
                    wait_back_menu()
class MultiRejoinTool:
    def __init__(self):
        self.instances = []
        self.is_running = False
        self.webhook_manager = WebhookManager()
        self.android_id_manager = AndroidIDManager()

    async def start(self):
        Utils.ensure_root()
        Utils.enable_wake_lock()

        os.system('clear' if os.name == 'posix' else 'cls')
        
        try:
            print(UIRenderer.render_title())
        except:
            print("""
╔═══════════════════════════════════════════════════════╗
║    🛒 𝗦𝗧𝗢𝗥𝗘𝟭𝗦.𝗖𝗢𝗠 • Premium E-Commerce Platform    ║
║         Your Trusted Shopping Destination            ║
║           Cửa Hàng Account Blox Fruit Uy tín S1 🇻🇳  ║
║           © 2024 STORE1S.COM • All Rights Reserved   ║
╚═══════════════════════════════════════════════════════╝""")

        print("\n🎯 Multi-Instance Roblox Rejoin Tool")
        print("1. 🚀 Bắt đầu auto rejoin")
        print("2. ⚙️ Setup packages")
        print("3. 🔧 Cấu hình Webhook Discord")
        print("4. 📱 Auto Change Android ID")
        print("5.  ❌ Log Out Account")
        print("6.  🍪 Login Cookie")

        choice = Utils.ask("\nChọn option (1-4): ")

        if choice.strip() == "1":
            await self.start_auto_rejoin()
        elif choice.strip() == "2":
            await self.setup_packages()
        elif choice.strip() == "3":
            self.webhook_manager.setup_webhook()
            input("\nNhấn Enter để tiếp tục...")
            await self.start()
        elif choice.strip() == "4":
            self.android_id_manager.android_id_menu()
            await self.start()
        elif choice.strip() == "5":
            logacc()
        elif choice.strip() == "6"
            login_cookie()
           
            
        else:
            print("❌ Lựa chọn không hợp lệ!")
            await asyncio.sleep(1)
            await self.start()

    async def setup_packages(self):
        print("\n🔍 Đang quét tất cả packages Roblox và Arya...")
        packages = Utils.detect_all_roblox_packages()
        
        if not packages:
            print("❌ Không tìm thấy package nào!")
            return

        print("\n📦 Tìm thấy các packages:")
        for index, pkg in enumerate(packages.values(), 1):
            print(f"{index}. {pkg['displayName']} ({pkg['packageName']})")

        configs = Utils.load_multi_configs()
        
        for package_name, package_info in packages.items():
            print(f"\n⚙️ Cấu hình cho {package_info['displayName']}")
            
            cookie = Utils.get_roblox_cookie(package_name)
            if not cookie:
                print(f"❌ Không lấy được cookie cho {package_name}, bỏ qua...")
                continue

            user = RobloxUser(cookie=cookie)
            user_id = await user.fetch_authenticated_user()
            
            if not user_id:
                print(f"❌ Không lấy được user info cho {package_name}, bỏ qua...")
                continue

            print(f"👤 Username: {user.username}")
            print(f"🆔 User ID: {user_id}")

            selector = GameSelector()
            game = await selector.choose_game()

            while True:
                try:
                    delay_input = Utils.ask("⏱️ Delay check (giây, 15-120): ")
                    delay_sec = int(delay_input)
                    if 15 <= delay_sec <= 120:
                        break
                    print("❌ Giá trị không hợp lệ! Vui lòng nhập lại.")
                except ValueError:
                    print("❌ Giá trị không hợp lệ! Vui lòng nhập lại.")

            configs[package_name] = {
                'username': user.username,
                'userId': user_id,
                'placeId': game['placeId'],
                'gameName': game['name'],
                'linkCode': game['linkCode'],
                'delaySec': delay_sec,
                'packageName': package_name
            }

            print(f"✅ Đã cấu hình xong cho {package_info['displayName']}!")

        Utils.save_multi_configs(configs)
        print("\n✅ Setup hoàn tất! Đã thêm tất cả các package Arya.")
        
        print("\n⏳ Đang quay lại menu chính...")
        await asyncio.sleep(2)
        await self.start()

    async def start_auto_rejoin(self):
        configs = Utils.load_multi_configs()

        if not configs:
            print("❌ Chưa có config nào! Vui lòng chạy setup packages trước.")
            await asyncio.sleep(2)
            await self.start()
            return

        print("\n📋 Danh sách packages đã cấu hình:")
        print(UIRenderer.display_configured_packages(configs))

        print("\n🎯 Chọn packages để chạy:")
        print("0. 🚀 Chạy tất cả packages")

        package_list = []
        for index, (package_name, config) in enumerate(configs.items(), start=1):
            if package_name == 'com.roblox.client':
                package_display = 'Global 🌍'
            elif package_name == 'com.roblox.client.vnggames':
                package_display = 'VNG 🇻🇳'
            elif package_name in ARYA_PACKAGES:
                version = package_name[-1].upper()
                package_display = f'Arya {version} 🔥'
            elif 'arya' in package_name.lower():
                package_display = 'Arya ⚡'
            else:
                package_display = package_name

            print(f"{index}. {package_display} ({config['username']})")
            package_list.append(package_name)

        choice = Utils.ask("\nNhập lựa chọn (0 để chạy tất cả, hoặc số cách nhau bởi khoảng trắng): ")
        
        if choice.strip() == "0":
            selected_packages = list(configs.keys())
            print("🚀 Sẽ chạy tất cả packages!")
        else:
            try:
                indices = [int(x) - 1 for x in choice.strip().split() 
                          if x.isdigit() and 0 <= int(x) - 1 < len(package_list)]
                
                if not indices:
                    print("❌ Lựa chọn không hợp lệ!")
                    await asyncio.sleep(1)
                    await self.start_auto_rejoin()
                    return

                selected_packages = [package_list[i] for i in indices]
                print("🎯 Sẽ chạy các packages:")
                for i, pkg in enumerate(selected_packages, 1):
                    print(f"  - {i}. {pkg}")
            except (ValueError, IndexError):
                print("❌ Lựa chọn không hợp lệ!")
                await asyncio.sleep(1)
                await self.start_auto_rejoin()
                return

        print("\n🚀 Khởi tạo multi-instance rejoin...")
        await self.initialize_selected_instances(selected_packages, configs)

    async def initialize_selected_instances(self, selected_packages: List[str], configs: Dict):
        for package_name in selected_packages:
            config = configs[package_name]
            cookie = Utils.get_roblox_cookie(package_name)
            
            if not cookie:
                print(f"❌ Không lấy được cookie cho {package_name}, bỏ qua...")
                continue

            user = RobloxUser(config['username'], config['userId'], cookie)
            status_handler = StatusHandler()

            self.instances.append({
                'packageName': package_name,
                'user': user,
                'config': config,
                'statusHandler': status_handler,
                'status': "Khởi tạo... 🔄",
                'info': "Đang chuẩn bị...",
                'countdown': "00s",
                'lastCheck': 0,
                'presenceType': "Unknown",
                'countdownSeconds': 0
            })

        if not self.instances:
            print("❌ Không có instance nào khả dụng!")
            return

        print(f"✅ Đã khởi tạo {len(self.instances)} instances!")
        print("⏳ Bắt đầu auto rejoin trong 3 giây...")
        await asyncio.sleep(3)
        
        self.is_running = True
        await self.run_multi_instance_loop()

    async def run_multi_instance_loop(self):
        render_counter = 0
        webhook_counter = 0

        while self.is_running:
            now = int(time.time() * 1000)

            for instance in self.instances:
                config = instance['config']
                user = instance['user']
                status_handler = instance['statusHandler']
                delay_ms = config['delaySec'] * 1000

                time_since_last_check = now - instance['lastCheck']

                time_left = max(0, delay_ms - time_since_last_check)
                instance['countdownSeconds'] = int((time_left + 999) // 1000)

                if time_since_last_check >= delay_ms:
                    presence = await user.get_presence()

                    presence_type_display = "Unknown"
                    if presence and 'userPresenceType' in presence:
                        presence_type_display = str(presence['userPresenceType'])

                    analysis = status_handler.analyze_presence(presence, config['placeId'])

                    if analysis['shouldLaunch']:
                        await GameLauncher.handle_game_launch(
                            analysis['shouldLaunch'],
                            config['placeId'],
                            config['linkCode'],
                            config['packageName'],
                            analysis['rejoinOnly']
                        )
                        status_handler.update_join_status(analysis['shouldLaunch'])

                    instance['status'] = analysis['status']
                    instance['info'] = analysis['info']
                    instance['presenceType'] = presence_type_display
                    instance['lastCheck'] = now

                if not instance.get('presenceType'):
                    instance['presenceType'] = "Unknown"

            if webhook_counter >= 30:
                asyncio.create_task(self.send_webhook_async())
                webhook_counter = 0
            else:
                webhook_counter += 1

            if render_counter % 5 == 0:
                os.system('clear' if os.name == 'posix' else 'cls')
                
                try:
                    print(UIRenderer.render_title())
                except:
                    print("""
╔═══════════════════════════════════════════════════════╗
║    🛒 𝗦𝗧𝗢𝗥𝗘𝟭𝗦.𝗖𝗢𝗠 • Premium E-Commerce Platform    ║
║         Your Trusted Shopping Destination            ║
║           Cửa Hàng Account Blox Fruit Uy tín S1 🇻🇳  ║
║           © 2024 STORE1S.COM • All Rights Reserved   ║
╚═══════════════════════════════════════════════════════╝""")

                print(UIRenderer.render_multi_instance_table(self.instances))

                if self.instances:
                    print("\n🔍 Debug (Instance 1):")
                    print(f"Package: {self.instances[0]['packageName']}")
                    print(f"Last Check: {datetime.fromtimestamp(self.instances[0]['lastCheck']/1000).strftime('%H:%M:%S')}")

                print("\n💡 Nhấn Ctrl+C để dừng chương trình")

            render_counter += 1
            await asyncio.sleep(1)

    async def send_webhook_async(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.webhook_manager.send_webhook, self.instances)


def signal_handler(signum, frame):
    print('\n\n🛑 Đang dừng chương trình...')
    print('👋 Cảm ơn bạn đã sử dụng Tool Ngân🎀')
    sys.exit(0)


async def main():
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        tool = MultiRejoinTool()
        await tool.start()
    except KeyboardInterrupt:
        print('\n\n🛑 Đang dừng chương trình...')
        print('👋 Cảm ơn bạn đã sử dụng Rejoin Ngan ❤')
        sys.exit(0)


if __name__ == "__main__":

    asyncio.run(main())
