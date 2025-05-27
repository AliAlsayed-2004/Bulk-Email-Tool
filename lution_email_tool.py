import requests
import json
import threading
from colorama import Fore, Style, init
import pyfiglet
import shutil
from time import sleep
import os
import sys
import argparse
from datetime import datetime
import hashlib
from getpass import getpass
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Initialize colorama
init(autoreset=True)

# Logging setup
LOG_DIR = "logs"
ERROR_LOG_FILE = os.path.join(LOG_DIR, "errors.log")
os.makedirs(LOG_DIR, exist_ok=True)

def log_error(message):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

# Load configuration
CONFIG_PATH = "config/config.json"
def load_config():
    default_config = {
        "API_BASE_URL": "https://api.lution.ee",
        "TIMEOUT": 10,
        "REQUEST_DELAY": 0.5,
        "MAX_THREADS": 20
    }
    if not os.path.exists(CONFIG_PATH):
        print(Fore.RED + f"[-] Configuration file not found: {CONFIG_PATH}")
        sys.exit(1)
    try:
        with open(CONFIG_PATH, 'r') as f:
            user_config = json.load(f)
        return {**default_config, **user_config}
    except Exception as e:
        log_error(f"Failed to load config: {str(e)}")
        print(Fore.RED + "[-] Failed to read configuration file.")
        sys.exit(1)

CONFIG = load_config()

class LutionEmailTool:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "Origin": "https://lution.ee",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        self.api_key = None
        self.lock = threading.Lock()
        self.running = True
        self.stats = {
            'total_purchased': 0,
            'total_attempts': 0,
            'start_time': datetime.now()
        }

    def load_api_key(self):
        self.api_key = os.getenv('LUTION_API_KEY')
        if self.api_key:
            return True
        if os.path.exists('config.enc'):
            try:
                with open('config.enc', 'rb') as f:
                    encrypted = f.read()
                key = hashlib.sha256(getpass("Enter decryption key: ").encode()).digest()
                self.api_key = bytes([encrypted[i] ^ key[i % len(key)] for i in range(len(encrypted))]).decode()
                return True
            except Exception as e:
                log_error(f"Decryption error: {str(e)}")
        self.api_key = getpass("Enter API key: ")
        if self.api_key and input("Save encrypted? (y/n): ").lower() == 'y':
            try:
                key = hashlib.sha256(getpass("Set encryption key: ").encode()).digest()
                encrypted = bytes([ord(self.api_key[i]) ^ key[i % len(key)] for i in range(len(self.api_key))])
                with open('config.enc', 'wb') as f:
                    f.write(encrypted)
            except Exception as e:
                log_error(f"Encryption error: {str(e)}")
        return bool(self.api_key)

    def display_logo(self):
        ascii_banner = pyfiglet.figlet_format("L u t i o n", "speed")
        colored_banner = f"{Fore.YELLOW}{Style.NORMAL}{ascii_banner}"
        terminal_width = shutil.get_terminal_size().columns
        centered_colored_banner = "     " + "\n".join([line.center(terminal_width) for line in colored_banner.split('\n')])
        cutter = '-' * 75
        logo = f"\n\n{centered_colored_banner}\n{cutter.center(terminal_width)}\n"
        print(logo)

    def save_credentials(self, data, filename="accounts.txt"):
        try:
            emails = data.get("Data", {}).get("Emails", [])
            if not emails:
                return 0
            with self.lock:
                with open(filename, "a", encoding='utf-8') as file:
                    for entry in emails:
                        email = entry.get("Email", "").strip()
                        password = entry.get("Password", "").strip()
                        if email and password:
                            file.write(f"{email}:{password}\n")
            return len(emails)
        except Exception as e:
            log_error(f"Error saving credentials: {str(e)}")
            print(Fore.RED + f"[-] Error saving credentials: {str(e)}")
            return 0

    def buy_email(self, mail_code, quantity, filename, success_list, proxy=None):
        session = requests.Session()
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        retry_strategy = Retry(total=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {self.api_key}"
        while len(success_list) < quantity and self.running:
            try:
                self.stats['total_attempts'] += 1
                response = session.get(
                    f"{CONFIG['API_BASE_URL']}/mail/buy",
                    params={"mailcode": mail_code, "quantity": 1},
                    headers=headers,
                    timeout=CONFIG['TIMEOUT']
                )
                if response.status_code == 200:
                    count = self.save_credentials(response.json(), filename)
                    if count > 0:
                        with self.lock:
                            success_list.extend([None] * count)
                            self.stats['total_purchased'] += count
                        print(Fore.GREEN + f"[+] Success: {len(success_list)}/{quantity}")
                elif response.status_code == 429:
                    print(Fore.YELLOW + "[!] Rate limited, slowing down...")
                    sleep(5)
                else:
                    print(Fore.RED + f"[-] Error {response.status_code}: {response.text}")
                sleep(CONFIG['REQUEST_DELAY'])
            except requests.exceptions.RequestException as e:
                log_error(f"Connection error: {str(e)}")
                print(Fore.RED + f"[-] Connection error: {str(e)}")
                sleep(2)

    def buy_emails(self, mail_code, quantity, thread_count, filename="accounts.txt", proxies=None):
        success_list = []
        threads = []
        print(Fore.CYAN + f"\n[*] Starting {thread_count} threads to purchase {quantity} {mail_code} emails...")
        for i in range(thread_count):
            proxy = proxies[i % len(proxies)] if proxies else None
            thread = threading.Thread(
                target=self.buy_email,
                args=(mail_code, quantity, filename, success_list, proxy),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        try:
            while len(success_list) < quantity and self.running:
                sleep(0.5)
                if len(success_list) % 10 == 0:
                    self.display_stats()
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[!] Stopping threads...")
            self.running = False
        finally:
            for thread in threads:
                thread.join()
            self.display_stats(final=True)
            print(Fore.GREEN + "\n[+] Operation completed.")

    def display_stats(self, final=False):
        elapsed = datetime.now() - self.stats['start_time']
        rate = self.stats['total_purchased'] / max(elapsed.total_seconds(), 1)
        stats_msg = (
            f"\n[STATS] Purchased: {self.stats['total_purchased']} | "
            f"Attempts: {self.stats['total_attempts']} | "
            f"Success Rate: {self.stats['total_purchased']/max(self.stats['total_attempts'],1)*100:.1f}% | "
            f"Elapsed: {str(elapsed).split('.')[0]} | "
            f"Rate: {rate:.2f}/sec"
        )
        print(Fore.CYAN + stats_msg)
        if final:
            with open(os.path.join(LOG_DIR, 'session_stats.log'), 'a') as f:
                f.write(f"{datetime.now()}: {stats_msg}\n")

    def menu(self):
        while self.running:
            try:
                print(Fore.BLUE + "\nMain Menu:")
                print(Fore.WHITE + "1. Buy Emails")
                print("2. View Statistics")
                print("3. Exit")
                choice = input(Fore.YELLOW + "\n[?] Select option: ").strip()
                if choice == "1":
                    self.buy_menu()
                elif choice == "2":
                    self.display_stats(final=True)
                elif choice == "3":
                    self.running = False
                else:
                    print(Fore.RED + "[-] Invalid choice")
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n[!] Returning to menu...")
            except Exception as e:
                log_error(f"Menu error: {str(e)}")
                print(Fore.RED + f"[-] Error: {str(e)}")

    def buy_menu(self):
        print(Fore.CYAN + "\nAvailable Mail Types:")
        print("1. HOTMAIL")
        print("2. OUTLOOK")
        mail_choice = input(Fore.YELLOW + "[?] Select mail type: ").strip()
        mail_code = {"1": "HOTMAIL", "2": "OUTLOOK"}.get(mail_choice)
        if not mail_code:
            print(Fore.RED + "[-] Invalid selection")
            return
        try:
            quantity = int(input(Fore.YELLOW + "[?] Quantity to purchase: "))
            thread_count = int(input(Fore.YELLOW + f"[?] Threads (1-{CONFIG['MAX_THREADS']}): "))
            thread_count = max(1, min(thread_count, CONFIG['MAX_THREADS']))
            filename = input(Fore.YELLOW + "[?] Output file [accounts.txt]: ").strip() or "accounts.txt"
            proxies = None
            if os.path.exists('proxies.txt'):
                with open('proxies.txt') as f:
                    proxies = [line.strip() for line in f if line.strip()]
            self.buy_emails(mail_code, quantity, thread_count, filename, proxies)
        except ValueError:
            print(Fore.RED + "[-] Please enter valid numbers")
        except Exception as e:
            log_error(f"Buy menu error: {str(e)}")
            print(Fore.RED + f"[-] Error: {str(e)}")

def main():
    tool = LutionEmailTool()
    tool.display_logo()
    parser = argparse.ArgumentParser(description='Lution Email Purchasing Tool')
    parser.add_argument('--cli', action='store_true', help='Run in command-line mode')
    parser.add_argument('--mail', choices=['HOTMAIL', 'OUTLOOK'], help='Mail type')
    parser.add_argument('--quantity', type=int, help='Number of emails to purchase')
    parser.add_argument('--threads', type=int, default=5, help='Number of threads')
    parser.add_argument('--output', help='Output filename')
    args = parser.parse_args()
    if not tool.load_api_key():
        print(Fore.RED + "[-] API key is required")
        return
    if args.cli or any([args.mail, args.quantity]):
        if not args.mail or not args.quantity:
            print(Fore.RED + "[-] --mail and --quantity are required in CLI mode")
            return
        tool.buy_emails(
            args.mail,
            args.quantity,
            args.threads,
            args.output or "accounts.txt"
        )
    else:
        tool.menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Application terminated by user")
        sys.exit(0)
    except Exception as e:
        log_error(f"Fatal error: {str(e)}")
        print(Fore.RED + f"\n[-] Critical error: {str(e)}")
        sys.exit(1)
