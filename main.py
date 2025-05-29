import os
import sys
import time
import base64
import socket
import platform
import getpass
import requests

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def rainbow_text(text):
    colors = [
        "\033[91m", "\033[93m", "\033[92m", "\033[96m",
        "\033[94m", "\033[95m", "\033[97m"
    ]
    reset = "\033[0m"
    result = ""
    for i, c in enumerate(text):
        result += colors[i % len(colors)] + c
    return result + reset

def machine_fingerprint():
    data = f"{socket.gethostname()}_{platform.node()}_{platform.machine()}"
    return data

def xor_encrypt_decrypt(data, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

def encode_key(machine_id, secret="Pay2RespondSecret"):
    xored = xor_encrypt_decrypt(machine_id, secret)
    return base64.urlsafe_b64encode(xored.encode()).decode()

def decode_key(encoded, secret="Pay2RespondSecret"):
    try:
        decoded = base64.urlsafe_b64decode(encoded).decode()
        return xor_encrypt_decrypt(decoded, secret)
    except Exception:
        return None

def save_key_file(key):
    with open(".keyfile", "w") as f:
        f.write(key)

def load_key_file():
    if os.path.exists(".keyfile"):
        with open(".keyfile", "r") as f:
            return f.read().strip()
    return None

def validate_key(key):
    decoded = decode_key(key)
    return decoded == machine_fingerprint()

def prompt_key():
    clear()
    print(rainbow_text("XBL Targeter - Paid Key Validation"))
    existing = load_key_file()
    if existing and validate_key(existing):
        return True
    print("You need a paid key to unlock advanced features.")
    key_input = getpass.getpass("Enter your paid key: ").strip()
    if validate_key(key_input):
        save_key_file(key_input)
        return True
    print("Invalid or mismatched key for this machine.")
    time.sleep(2)
    return False

def print_header(title, gamertag, xbl_token, expires_in, paid):
    clear()
    print(rainbow_text(f"=== {title} ==="))
    print(f"Gamertag: {gamertag if gamertag else 'N/A'} | XBL Token: {'Authenticated' if xbl_token else 'Not Authenticated'} | Expires in: {expires_in} seconds")
    print(f"Credits: Pay2Respond | Discord: Pay2Respond#0001 | GitHub: Pay2Respond | TikTok: Pay2Respond")
    print(f"Paid Features: {'Enabled' if paid else 'Disabled'}")
    print("")

def validate_xbl_token(token):
    if not token.startswith("XBL3.0 x="):
        return False
    return True

def get_xuid(token):
    headers = {"Authorization": token}
    try:
        # Peoplehub expects XUID first, but we get it from token exchange normally
        # Here we simulate XUID retrieval from token (in real flow, must exchange token)
        url = "https://peoplehub.xboxlive.com/users/me/profile/settings"
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        for setting in data.get("profileUsers", [{}])[0].get("settings", []):
            if setting.get("id") == "GameDisplayName":
                display_name = setting.get("value")
        # Usually you get xuid from the token exchange step, simulate here with placeholder
        # But since no API, store dummy for demonstration
        xuid = "0000000000000000"
        return xuid, display_name
    except:
        return None, None

def main_menu(paid, gamertag, token, token_expiry):
    while True:
        expires_in = max(0, int(token_expiry - time.time()))
        if expires_in == 0:
            return False, None, None

        print_header("XBL Targeter - Main Menu", gamertag, token, expires_in, paid)
        print("1) Party Tools")
        print("2) Account Tools")
        if paid:
            print("3) Overpowered Paid Feature 1")
            print("4) Overpowered Paid Feature 2")
        print("0) Exit")
        choice = input("Select an option: ").strip()
        if choice == "0":
            sys.exit(0)
        elif choice in ["1", "2"]:
            print(f"Feature {choice} coming soon...")
            input("Press Enter to return to main menu...")
        elif choice == "3" and paid:
            print("Paid Feature 1 running...")
            input("Press Enter to return to main menu...")
        elif choice == "4" and paid:
            print("Paid Feature 2 running...")
            input("Press Enter to return to main menu...")
        else:
            print("Invalid choice")
            time.sleep(1)

def get_token_input():
    clear()
    print(rainbow_text("XBL Targeter - Token Input"))
    token = input("Enter your XBL 3.0 Token (starts with 'XBL3.0 x='): ").strip()
    if not validate_xbl_token(token):
        print("Invalid token format.")
        time.sleep(2)
        return None
    return token

def token_auth_flow():
    while True:
        token = get_token_input()
        if not token:
            continue
        xuid, display_name = get_xuid(token)
        if not xuid or not display_name:
            print("Failed to authenticate token or fetch profile.")
            time.sleep(2)
            continue
        print(f"Welcome, {display_name}!")
        time.sleep(2)
        return token, display_name

def main():
    paid = False
    gamertag = None
    token = None
    token_expiry = 0

    while True:
        token, gamertag = token_auth_flow()
        token_expiry = time.time() + (13 * 3600)

        if not token:
            continue

        clear()
        print(f"Authenticated as {gamertag}")
        time.sleep(1)

        paid = prompt_key()

        success = main_menu(paid, gamertag, token, token_expiry)
        if not success:
            print("Token expired. Please re-authenticate.")
            time.sleep(2)

if __name__ == "__main__":
    main()
