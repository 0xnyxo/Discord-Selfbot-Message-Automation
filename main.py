import requests
import random
import json
import threading
import time
import sys
import toml
import os


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    GRAY = "\033[90m"
    PINK = "\033[95m"


class ProxyHandler:
    def __init__(self, proxy_file):
        self.proxies = self.load_proxies(proxy_file)

    def load_proxies(self, proxy_file):
        with open(proxy_file, "r") as f:
            return [line.strip() for line in f.readlines()]

    def get_random_proxy(self):
        if self.proxies:
            return random.choice(self.proxies)
        return None


class DiscordSelfuser:
    def __init__(
        self,
        user_tokens,
        guild_id,
        proxy_handler,
        use_proxies=False,
        multitokens=False,
        use_image=False,
    ):
        self.user_tokens = user_tokens if multitokens else [user_tokens[0]]
        self.guild_id = guild_id
        self.proxy_handler = proxy_handler
        self.use_proxies = use_proxies
        self.success_count = 0
        self.failed_count = 0
        self.start_time = None
        self.multitokens = multitokens
        self.token_index = 0
        self.use_image = use_image

    def get_headers(self):
        token = self.get_token()
        return {
            "Authorization": f"{token}",
        }

    def get_token(self):
        if self.multitokens:
            token = self.user_tokens[self.token_index]
            print(
                f"{Colors.GRAY}[INFO] Using token {self.token_index + 1}/{len(self.user_tokens)}: {token[:10]}...{Colors.ENDC}"
            )
            self.token_index = (self.token_index + 1) % len(self.user_tokens)
            return token
        return self.user_tokens[0]

    def get_channels(self):
        url = f"https://discord.com/api/v9/guilds/{self.guild_id}/channels"
        headers = self.get_headers()
        proxies = self.get_proxies()

        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            channels = response.json()
            return [channel for channel in channels if channel["type"] == 0]
        elif response.status_code == 403:
            print(
                f"{Colors.FAIL}↳ Unauthorized (403): Failed to retrieve channels. Please check account permissions.{Colors.ENDC}"
            )
        elif response.status_code == 401:
            print(
                f"{Colors.FAIL}↳ Invalid Token (401): Failed to retrieve channels. Please check your user token.{Colors.ENDC}"
            )
        else:
            print(
                f"{Colors.PINK}↳ Failed to retrieve channels: {response.status_code} - {response.text}{Colors.ENDC}"
            )
        return []

    def send_message(self, channel_id, message):
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        headers = self.get_headers()
        proxies = self.get_proxies()

        data = {"content": message}

        if self.use_image:
            FILE_NAME = "image1.jpg"
            FILE_PATH = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "data", FILE_NAME
            )
            try:
                with open(FILE_PATH, "rb") as file:
                    files = {
                        "file": (file.name, file),
                    }
                    response = requests.post(
                        url, headers=headers, data=data, files=files, proxies=proxies
                    )

            except FileNotFoundError:
                print(f"{Colors.FAIL}↳ File not found: {FILE_PATH}{Colors.ENDC}")
                return
        else:
            response = requests.post(url, headers=headers, json=data, proxies=proxies)

        current_time = time.strftime("%H:%M")
        if response.status_code == 200:
            self.success_count += 1
            print(f"{Colors.GRAY}[{current_time}] {Colors.ENDC}✔️ ↳ Request Sent")
        else:
            self.failed_count += 1
            print(
                f"{Colors.PINK}[{current_time}] ⛌ ↳ Failed To Send. Status Code: {response.status_code} - {response.text}{Colors.ENDC}"
            )

    def get_proxies(self):
        if self.use_proxies:
            proxy = self.proxy_handler.get_random_proxy()
            if proxy:
                return {"http": proxy, "https": proxy}
        return None

    def update_title(self, num_threads):
        while True:
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            requests_per_second = (
                self.success_count / elapsed_time if elapsed_time > 0 else 0
            )
            title = f"» Vyxooo | Success: {self.success_count} | Failed: {self.failed_count} | Threads: {num_threads} | Requests/s: {requests_per_second:.2f}"
            sys.stdout.write(f"\x1b]2;{title}\x07")
            time.sleep(1)


class userController:
    def __init__(self, discord_selfuser, num_threads):
        self.discord_selfuser = discord_selfuser
        self.num_threads = num_threads
        self.threads = []

    def start_worker(self, channel_id, message):
        thread = threading.Thread(target=self.worker, args=(channel_id, message))
        self.threads.append(thread)
        thread.start()

    def worker(self, channel_id, message):
        self.discord_selfuser.send_message(channel_id, message)

    def run(self, channels, message):
        title_thread = threading.Thread(
            target=self.discord_selfuser.update_title, args=(self.num_threads,)
        )
        title_thread.daemon = True
        title_thread.start()
        while True:
            for channel in channels:
                self.start_worker(channel["id"], message)
                if len(self.threads) >= self.num_threads:
                    for thread in self.threads:
                        thread.join()
                    self.threads = []
            for thread in self.threads:
                thread.join()

        print("↳ All messages sent.")


def print_logo():
    logo = f"""
{Colors.OKGREEN}
    ┌┐┌  ┬ ┬  ─┐ ┬  ┌─┐
    │││  └┬┘  ┌┴┬┘  │ │
    ┘└┘   ┴   ┴ └─  └─┘
{Colors.ENDC}"""
    print(logo)


def get_user_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\n↳ Process interrupted by user.")
        sys.exit()


def load_tokens(file_path):
    with open(file_path, "r") as f:
        tokens = [line.strip() for line in f.readlines()]
    if not tokens:
        print(f"{Colors.FAIL}↳ No tokens found in {file_path}.{Colors.ENDC}")
        sys.exit()
    return tokens


if __name__ == "__main__":
    print_logo()
    config = toml.load("cfg/settings.toml")

    token_file_path = "cfg/tokens.txt"
    user_tokens = load_tokens(token_file_path)
    multitokens = config["config"]["multitokens"]
    guild_id = config["server"]["guild_id"]
    use_proxies = config["proxy"]["use_proxies"]
    proxy_file = config["proxy"]["proxy_file"]
    num_threads = config["config"]["num_threads"]
    message = config["config"]["message"]
    custom_channel_id = config["config"]["custom_channel_id"]
    use_image = config["config"]["use_image"]

    proxy_handler = ProxyHandler(proxy_file)
    discord_selfuser = DiscordSelfuser(
        user_tokens, guild_id, proxy_handler, use_proxies, multitokens, use_image
    )

    if custom_channel_id:
        channels = [{"id": custom_channel_id}]
    else:
        channels = discord_selfuser.get_channels()
        if not channels:
            print(
                f"{Colors.PINK}↳ No channels found or unauthorized access.{Colors.ENDC}"
            )
            sys.exit()

    user_controller = userController(discord_selfuser, num_threads)
    user_controller.run(channels, message)
