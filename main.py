import requests
import os
import time
import threading
import base64
import socket
import platform
import sys

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def obscure_secret():
    return [81, 98, 122, 51, 83, 102, 116, 113, 112, 111, 101, 84, 102, 100, 115, 102, 117]

def deobscure_secret(codes):
    return "".join(chr(c - 1) for c in codes)

def xor_encrypt_decrypt(data, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

def machine_fingerprint():
    return f"{socket.gethostname()}_{platform.node()}_{platform.machine()}"

def validate_key(input_key):
    mf = machine_fingerprint()
    secret = deobscure_secret(obscure_secret())
    expected = base64.urlsafe_b64encode(xor_encrypt_decrypt(mf, secret).encode()).decode()
    return input_key.strip() == expected

def rainbow_text(text):
    colors = [
        '\033[91m', '\033[93m', '\033[92m', '\033[96m',
        '\033[94m', '\033[95m', '\033[91m'
    ]
    reset = '\033[0m'
    result = ''
    for i, c in enumerate(text):
        result += colors[i % len(colors)] + c
    return result + reset

def print_header(menu_title, token_status, gamertag, time_left, paid):
    clear()
    print(rainbow_text(f"=== XBL Targeter - {menu_title} ==="))
    print(f"Credits: Pay2Respond | Discord: Pay2Respond#0000 | GitHub: Pay2Respond | TikTok: Pay2Respond")
    print(f"Token Status: {token_status} | Gamertag: {gamertag if gamertag else 'N/A'} | Token expires in: {time_left}")
    print(f"Paid Features: {'Unlocked' if paid else 'Locked'}")
    print("=" * 50)
    print()

def get_xsts_token(xbl_token):
    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    headers = {"Content-Type": "application/json"}
    payload = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [xbl_token]
        },
        "RelyingParty": "http://xboxlive.com",
        "TokenType": "JWT"
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 200:
        return r.json().get("Token"), r.json().get("DisplayClaims", {}).get("xui", [{}])[0].get("xid")
    return None, None

def get_user_info(xuid, xsts_token):
    url = f"https://peoplehub.xboxlive.com/users/me/people/xuids({xuid})/decoration/detail,preferredColor,presenceDetail"
    headers = {
        "x-xbl-contract-version": "2",
        "Authorization": f"XBL3.0 x={xuid};{xsts_token}"
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data.get("people"):
            p = data["people"][0]
            display_name = p.get("DisplayName", "N/A")
            presence = p.get("presenceDetail", {}).get("state", "Unknown")
            gamerscore = p.get("gamerscore", "N/A")
            return display_name, presence, gamerscore
    return None, None, None

def input_token_loop():
    while True:
        clear()
        print(rainbow_text("=== XBL Targeter - Enter XBL 3.0 Token ==="))
        token = input("Type your XBL 3.0 Token (starting with 'XBL3.0 x='): ").strip()
        if not token.startswith("XBL3.0 x="):
            print("Invalid format. Token must start with 'XBL3.0 x='.")
            time.sleep(2)
            continue

        xbl_token = token[len("XBL3.0 x="):].split(";")[1] if ";" in token[len("XBL3.0 x="):] else token[len("XBL3.0 x="):]

        xsts_token, xuid = get_xsts_token(xbl_token)
        if xsts_token and xuid:
            display_name, presence, gamerscore = get_user_info(xuid, xsts_token)
            if display_name:
                return token, xsts_token, xuid, display_name, presence, gamerscore
            else:
                print("Failed to retrieve user info. Try again.")
                time.sleep(2)
        else:
            print("Failed to validate token. Try again.")
            time.sleep(2)

def countdown_timer(expiry_seconds, stop_event):
    start = time.time()
    while not stop_event.is_set():
        elapsed = time.time() - start
        left = max(0, int(expiry_seconds - elapsed))
        mins, secs = divmod(left, 60)
        hours, mins = divmod(mins, 60)
        time_left = f"{hours:02d}:{mins:02d}:{secs:02d}"
        yield time_left
        time.sleep(1)

def prompt_paid_key():
    clear()
    print(rainbow_text("=== XBL Targeter - Paid Key ==="))
    yn = input("Do you have a paid key? (y/n): ").strip().lower()
    if yn == 'y':
        key = input("Enter your paid key: ").strip()
        if validate_key(key):
            return True
        else:
            print("Invalid key.")
            time.sleep(2)
            return False
    return False

def main_menu(paid):
    menu_title = "Main Menu"
    options = [
        "1. Party Tools",
        "2. Account Tools",
        "3. Paid Features",
        "4. Exit"
    ]
    while True:
        print_header(menu_title, "Authenticated", gamertag, token_time_left, paid)
        for option in options:
            if option.startswith("3.") and not paid:
                print(option + " [Locked]")
            else:
                print(option)
        choice = input("\nSelect option: ").strip()
        if choice == "1":
            party_tools_menu(paid)
        elif choice == "2":
            account_tools_menu(paid)
        elif choice == "3":
            if paid:
                paid_features_menu()
            else:
                print("Paid features locked. Get a key from Pay2Respond on Discord.")
                time.sleep(2)
        elif choice == "4":
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid choice.")
            time.sleep(1)

def party_tools_menu(paid):
    menu_title = "Party Tools"
    while True:
        print_header(menu_title, "Authenticated", gamertag, token_time_left, paid)
        print("Party tools coming soon...")
        print("0. Back to main menu")
        choice = input("Select option: ").strip()
        if choice == "0":
            return

def account_tools_menu(paid):
    menu_title = "Account Tools"
    while True:
        print_header(menu_title, "Authenticated", gamertag, token_time_left, paid)
        print(f"Gamertag: {gamertag}")
        print(f"Presence: {presence}")
        print(f"Gamerscore: {gamerscore}")
        print("0. Back to main menu")
        choice = input("Select option: ").strip()
        if choice == "0":
            return

def paid_features_menu():
    menu_title = "Paid Features"
    while True:
        print_header(menu_title, "Authenticated", gamertag, token_time_left, True)
        print("Paid features coming soon...")
        print("0. Back to main menu")
        choice = input("Select option: ").strip()
        if choice == "0":
            return

if __name__ == "__main__":
    token, xsts_token, xuid, gamertag, presence, gamerscore = None, None, None, None, None, None
    token_expiry_seconds = 13 * 3600
    stop_timer = threading.Event()

    while True:
        token, xsts_token, xuid, gamertag, presence, gamerscore = input_token_loop()
        token_time_left = "13:00:00"
        paid = False
        if prompt_paid_key():
            paid = True

        stop_timer.clear()
        def timer_thread():
            global token_time_left
            for t_left in countdown_timer(token_expiry_seconds, stop_timer):
                token_time_left = t_left
                if t_left == "00:00:00":
                    stop_timer.set()
                    break

        threading.Thread(target=timer_thread, daemon=True).start()
        main_menu(paid)
