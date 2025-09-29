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
import threading  # NEW: Added for Android ID functionality

# Try to install required packages
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

# NEW: Android ID Manager Class
class AndroidIDManager:
    def __init__(self):
        self.auto_android_id_enabled = False
        self.auto_android_id_thread = None
        self.auto_android_id_value = None

    def set_android_id(self, android_id):
        """
        Set Android ID using subprocess command
        """
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
        """
        Continuously change Android ID every 2 seconds while enabled
        """
        while self.auto_android_id_enabled:
            if self.auto_android_id_value:
                success = self.set_android_id(self.auto_android_id_value)
                if not success:
                    print("\033[1;33m[ Tool ] - Retrying Android ID change...\033[0m")
            time.sleep(2)  # Wait 2 seconds between changes

    def start_auto_android_id(self):
        """
        Start the auto Android ID change functionality
        """
        if self.auto_android_id_enabled:
            print("\033[1;33m[ Tool ] - Auto Android ID change is already running!\033[0m")
            return False
        
        # Get Android ID from user input
        android_id = input("\033[1;93m[ Tool ] - Enter Android ID to continuously set: \033[0m").strip()
        
        if not android_id:
            print("\033[1;31m[ Tool ] - Android ID cannot be empty.\033[0m")
            return False
        
        # Validate Android ID format (basic check)
        if len(android_id) < 16:
            print("\033[1;33m[ Tool ] - Warning: Android ID seems too short. Continue? (y/n): \033[0m", end="")
            confirm = input().strip().lower()
            if confirm != 'y':
                return False
        
        self.auto_android_id_value = android_id
        self.auto_android_id_enabled = True
        
        # Start the background thread
        if self.auto_android_id_thread is None or not self.auto_android_id_thread.is_alive():
            self.auto_android_id_thread = threading.Thread(target=self.auto_change_android_id, daemon=True)
            self.auto_android_id_thread.start()
        
        print(f"\033[1;32m[ Tool ] - Auto Android ID change enabled with ID: {android_id}\033[0m")
        print(f"\033[1;32m[ Tool ] - Android ID will be set every 2 seconds\033[0m")
        return True

    def stop_auto_android_id(self):
        """
        Stop the auto Android ID change functionality
        """
        if not self.auto_android_id_enabled:
            print("\033[1;33m[ Tool ] - Auto Android ID change is not running.\033[0m")
            return False
        
        self.auto_android_id_enabled = False
        print("\033[1;31m[ Tool ] - Auto Android ID change disabled.\033[0m")
        return True

    def toggle_auto_android_id(self):
        """
        Toggle the auto Android ID change functionality on/off
        """
        if not self.auto_android_id_enabled:
            return self.start_auto_android_id()
        else:
            return self.stop_auto_android_id()

    def get_auto_android_id_status(self):
        """
        Get current status of auto Android ID functionality
        """
        status = {
            "enabled": self.auto_android_id_enabled,
            "android_id": self.auto_android_id_value if self.auto_android_id_value else "Not set",
            "thread_alive": self.auto_android_id_thread.is_alive() if self.auto_android_id_thread else False
        }
        
        return status

    def get_current_android_id(self):
        """
        Get the current Android ID from the system
        """
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
        """
        Interactive menu for Android ID management
        """
        while True:
            print("\n" + "="*50)
            print("\033[1;34m[ ANDROID ID MANAGER ]\033[0m")
            print("="*50)
            
            # Display current status
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

# NEW: Webhook Manager Class
class WebhookManager:
    def __init__(self):
        self.webhook_url = None
        self.device_name = None
        self.interval = None
        self.enabled = False
        self.last_sent_time = 0
        self.load_config()

    def load_config(self):
        """Load webhook configuration from file"""
        try:
            if WEBHOOK_CONFIG_PATH.exists():
                with open(WEBHOOK_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.webhook_url = config.get('webhook_url')
                    self.device_name = config.get('device_name', 'Unknown Device')
                    self.interval = config.get('interval', 60)  # minutes
                    self.enabled = config.get('enabled', False) and self.webhook_url
        except Exception as e:
            print(f"❌ Lỗi load webhook config: {e}")

    def save_config(self):
        """Save webhook configuration to file"""
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
        """Setup webhook configuration"""
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
        """Capture screenshot using screencap command"""
        try:
            screenshot_path = "/data/data/com.termux/files/home/screenshot.png"
            # Try multiple screencap methods
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
        """Get system information for webhook"""
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
        """Get system uptime"""
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
        """Send webhook with system info and screenshot"""
        if not self.enabled or not self.webhook_url:
            return False

        try:
            # Check if enough time has passed since last send
            current_time = time.time()
            if current_time - self.last_sent_time < self.interval * 60:
                return False

            print("📊 Đang gửi webhook...")
            
            # Capture screenshot
            screenshot_path = self.capture_screenshot()
            
            # Get system info
            system_info = self.get_system_info()
            if not system_info:
                return False

            # Prepare instances info
            instances_info = ""
            if instances:
                for i, instance in enumerate(instances, 1):
                    package_name = instance.get('packageName', 'Unknown')
                    status = instance.get('status', 'Unknown')
                    username = instance.get('config', {}).get('username', 'Unknown')
                    
                    # Mask username for privacy
                    masked_username = username[:3] + "***" if len(username) > 3 else username
                    
                    instances_info += f"{i}. {package_name} ({masked_username}) - {status}\n"
            else:
                instances_info = "Không có instances đang chạy"

            # Create embed
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

            # Prepare payload
            payload = {
                "embeds": [embed],
                "username": "Rejoin By Ngan🔥",
                "avatar_url": "https://cdn.discordapp.com/attachments/1269331861902196902/1422144505485721653/1.png?ex=68db9ac8&is=68da4948&hm=a7ed4d0a5740ff876e12b22f94f3e14df81d5396fb504b52251f1382e65d1211&"
            }

            # Send webhook
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
                
                # Clean up screenshot file
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

class Utils:
    @staticmethod
    def ensure_root():
        try:
            if os.getuid() != 0:
                print("Cần quyền root, chuyển qua su...")
                # Dùng full path để tránh lỗi môi trường PATH khi su
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
            # Đợi 1 giây để đảm bảo app đã đóng hoàn toàn
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

        # Determine activity based on package
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
            result = subprocess.run("pm list packages | grep com.roblox", 
                                  shell=True, capture_output=True, text=True)
            lines = [line for line in result.stdout.split('\n') if 'com.roblox' in line]
            
            for line in lines:
                match = re.search(r'package:(com\.roblox[^\s]+)', line)
                if match:
                    package_name = match.group(1)
                    
                    if package_name == 'com.roblox.client':
                        display_name = 'Roblox Quốc tế 🌍'
                    elif package_name == 'com.roblox.client.vnggames':
                        display_name = 'Roblox VNG 🇻🇳'
                    else:
                        display_name = f'Roblox Custom ({package_name}) 🎮'
                    
                    packages[package_name] = {
                        'packageName': package_name,
                        'displayName': display_name
                    }
        except Exception as e:
            print(f"❌ Lỗi khi quét packages: {e}")

        return packages

    @staticmethod
    def get_roblox_cookie(package_name: str) -> Optional[str]:
        print(f"🍪 [{package_name}] Đang lấy cookie ROBLOSECURITY...")
        
        try:
            # First method
            cmd = f"cat /data/data/{package_name}/app_webview/Default/Cookies | strings | grep ROBLOSECURITY"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            raw = result.stdout
        except:
            try:
                # Second method with su
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
                # Đồng bộ kill app trước
                await Utils.kill_app(package_name)
            else:
                print(f"⚠️ [{package_name}] RejoinOnly mode - không kill app")

            # Sau đó mới launch
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
            "1": ["126884695634066", "Grow-a-Garden 🌱"],
            "2": ["2753915549", "Blox-Fruits 🍇"],
            "3": ["6284583030", "Pet-Simulator-X 🐾"],
            "4": ["126244816328678", "DIG ⛏️"],
            "5": ["116495829188952", "Dead-Rails-Alpha 🚂"],
            "6": ["8737602449", "PLS-DONATE 💰"],
            "0": ["custom", "Tùy chỉnh ⚙️"],
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
        now = int(time.time() * 1000)  # milliseconds

        if not presence or presence.get('userPresenceType') is None:
            return {
                'status': "Không rõ ❓",
                'info': "Không lấy được trạng thái hoặc thiếu rootPlaceId",
                'shouldLaunch': True,  # Always try to rejoin when presence is unclear
                'rejoinOnly': False
            }

        # User is offline or away
        if presence.get('userPresenceType') in [0, 1]:
            return {
                'status': "Offline 💤",
                'info': "User offline! Tiến hành rejoin! 🚀",
                'shouldLaunch': True,  # Always rejoin when offline
                'rejoinOnly': False
            }

        # User is not in game (online but not playing)
        if presence.get('userPresenceType') != 2:
            return {
                'status': "Không online 😴",
                'info': "User không trong game. Đã mở lại game! 🎮",
                'shouldLaunch': True,  # Always rejoin when not in game
                'rejoinOnly': False
            }

        # User is in game but wrong place
        root_place_id = presence.get('rootPlaceId')
        if not root_place_id or str(root_place_id) != str(target_root_place_id):
            return {
                'status': "Sai map 🗺️",
                'info': f"User đang trong game nhưng sai rootPlaceId ({root_place_id}). Đã rejoin đúng map! 🎯",
                'shouldLaunch': True,
                'rejoinOnly': True
            }

        # User is in correct game
        return {
            'status': "Online ✅",
            'info': "Đang ở đúng game 🎮",
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
║           Cửa Hàng Account Blox Fruit Uy tín S1 🇻🇳                                        ║
║           © 2024 STORE1S.COM • All Rights Reserved   ║
╚═══════════════════════════════════════════════════════╝"""
        try:
            try:
                title = pyfiglet.figlet_format("STORE1ST.COM", font="slant")
            except Exception:
                console.print("[yellow]⚠️ Font 'small' lỗi, dùng font mặc định[/yellow]")
                title = pyfiglet.figlet_format("STORE1ST.COM")
            
            with console.capture() as capture:
                console.print(title + "\n🚀 REJOIN TOOL 🚀", style="cyan")
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
                package_display = {
                    'com.roblox.client': 'Global 🌍',
                    'com.roblox.client.vnggames': 'VNG 🇻🇳'
                }.get(instance.get('packageName', ''), instance.get('packageName', 'Unknown'))

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
                package_display = {
                    'com.roblox.client': 'Global 🌍',
                    'com.roblox.client.vnggames': 'VNG 🇻🇳'
                }.get(package_name, package_name)

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

class MultiRejoinTool:
    def __init__(self):
        self.instances = []
        self.is_running = False
        self.webhook_manager = WebhookManager()
        self.android_id_manager = AndroidIDManager()  # NEW: Android ID Manager

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
║           Cửa Hàng Account Blox Fruit Uy tín S1 🇻🇳                                      ║
║           © 2024 STORE1S.COM • All Rights Reserved   ║
╚═══════════════════════════════════════════════════════╝""")

        print("\n🎯 Multi-Instance Roblox Rejoin Tool")
        print("1. 🚀 Bắt đầu auto rejoin")
        print("2. ⚙️ Setup packages")
        print("3. 🔧 Cấu hình Webhook Discord")
        print("4. 📱 Auto Change Android ID")  # NEW: Android ID option

        choice = Utils.ask("\nChọn option (1-4): ")

        if choice.strip() == "1":
            await self.start_auto_rejoin()
        elif choice.strip() == "2":
            await self.setup_packages()
        elif choice.strip() == "3":
            self.webhook_manager.setup_webhook()
            input("\nNhấn Enter để tiếp tục...")
            await self.start()
        elif choice.strip() == "4":  # NEW: Android ID Manager
            self.android_id_manager.android_id_menu()
            await self.start()
        else:
            print("❌ Lựa chọn không hợp lệ!")
            await asyncio.sleep(1)
            await self.start()

    async def setup_packages(self):
        print("\n🔍 Đang quét tất cả packages Roblox...")
        packages = Utils.detect_all_roblox_packages()
        
        if not packages:
            print("❌ Không tìm thấy package Roblox nào!")
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
        print("\n✅ Setup hoàn tất!")
        
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
        # Initialize instances chỉ cho các packages được chọn
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
            now = int(time.time() * 1000)  # milliseconds

            for instance in self.instances:
                config = instance['config']
                user = instance['user']
                status_handler = instance['statusHandler']
                delay_ms = config['delaySec'] * 1000

                time_since_last_check = now - instance['lastCheck']

                # Đếm ngược còn bao nhiêu giây nữa thì check lại
                time_left = max(0, delay_ms - time_since_last_check)
                instance['countdownSeconds'] = int((time_left + 999) // 1000)  # Ceiling division

                # Nếu đủ thời gian thì check
                if time_since_last_check >= delay_ms:
                    presence = await user.get_presence()

                    # Ghi lại type để hiển thị
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

                # Nếu chưa check lần nào hoặc chưa set presenceType thì giữ "Unknown"
                if not instance.get('presenceType'):
                    instance['presenceType'] = "Unknown"

            # NEW: Send webhook every 30 iterations (approximately every 30 seconds)
            if webhook_counter >= 30:
                # Run webhook in background to not block the main loop
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
║           Cửa Hàng Account Blox Fruit Uy tín S1 🇻🇳                                          ║
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
        """Send webhook asynchronously"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.webhook_manager.send_webhook, self.instances)


def signal_handler(signum, frame):
    print('\n\n🛑 Đang dừng chương trình...')
    print('👋 Cảm ơn bạn đã sử dụng Dawn Rejoin Tool!')
    sys.exit(0)


async def main():
    # Handle graceful shutdown
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