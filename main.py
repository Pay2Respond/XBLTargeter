import requests
import time
import sys
import os

xbl_token = None
xuid = None
gamertag = None
token_auth_time = 0
paid_user = False

def rainbow_text(text):
    colors = [
        "\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"
    ]
    result = ""
    for i, c in enumerate(text):
        result += colors[i % len(colors)] + c
    result += "\033[0m"
    return result

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(menu_title):
    clear_screen()
    print(rainbow_text("=== XBL Targeter ==="))
    print(f"Menu: {menu_title}")
    print("Credits: Pay2Respond | Discord: Pay2Respond | Github: Pay2Respond | TikTok: Pay2Respond")
    if xbl_token and time.time() - token_auth_time < 13 * 3600:
        print(f"Status: Authenticated | Gamertag: {gamertag} | XUID: {xuid}")
        remaining = int(13 * 3600 - (time.time() - token_auth_time))
        m, s = divmod(remaining, 60)
        h, m = divmod(m, 60)
        print(f"Token expires in: {h:02d}:{m:02d}:{s:02d}")
    else:
        print("Status: Not authenticated")
    print(f"Paid features: {'Unlocked' if paid_user else 'Locked'}")
    print()

def exchange_xts_token(xbl_token):
    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    headers = {"Content-Type": "application/json"}
    payload = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [xbl_token.replace("XBL3.0 ", "")]
        },
        "RelyingParty": "http://xboxlive.com",
        "TokenType": "JWT"
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        j = r.json()
        return j.get("DisplayClaims", {}).get("xui", [{}])[0]
    except:
        return None

def validate_token(token, xui):
    global xuid, gamertag
    xuid = xui.get("xid")
    if not xuid:
        return False
    url = f"https://peoplehub.xboxlive.com/users/xuids({xuid})/profile/settings"
    headers = {
        "Authorization": token,
        "x-xbl-contract-version": "2"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return False
        data = r.json()
        profile_users = data.get("profileUsers", [])
        if not profile_users:
            return False
        user_info = profile_users[0]
        xuid = user_info.get("id")
        settings = user_info.get("settings", [])
        gamertag = None
        for s in settings:
            if s.get("id") == "Gamertag":
                gamertag = s.get("value")
                break
        return bool(gamertag and xuid)
    except:
        return False

def check_key():
    global paid_user
    print("Paid features are locked. Do you have a paid key? (y/n)")
    answer = input(">> ").strip().lower()
    if answer == "y":
        print("Enter your paid key:")
        key = input(">> ").strip()
        from keygen import validate_key
        if validate_key(key):
            paid_user = True
            print("Paid features unlocked.")
            time.sleep(1)
            return
        print("Invalid key.")
        time.sleep(1)
    paid_user = False

def input_token_screen():
    global xbl_token, token_auth_time
    while True:
        print_header("Please input your XBL3.0 token")
        token = input("XBL3.0 Token (must start with 'XBL3.0 x='): ").strip()
        if not token.startswith("XBL3.0 x="):
            print("Invalid token format. Try again.")
            time.sleep(1)
            continue
        xui = exchange_xts_token(token)
        if not xui:
            print("Failed to authorize token. Try again.")
            time.sleep(1)
            continue
        if not validate_token(token, xui):
            print("Failed to fetch user info. Try again.")
            time.sleep(1)
            continue
        xbl_token = token
        token_auth_time = time.time()
        break

def main_menu():
    while True:
        if not xbl_token or time.time() - token_auth_time > 13 * 3600:
            global paid_user
            paid_user = False
            input_token_screen()
            check_key()
        print_header("Main Menu")
        print("1. Party Tools")
        print("2. Account Tools")
        print("3. Paid Feature 1")
        print("4. Paid Feature 2")
        print("5. Exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            party_tools()
        elif choice == "2":
            account_tools()
        elif choice == "3":
            if not paid_user:
                print("Paid features locked. Enter key? (y/n)")
                yn = input(">> ").strip().lower()
                if yn == "y":
                    check_key()
                else:
                    continue
            if paid_user:
                paid_feature_1()
        elif choice == "4":
            if not paid_user:
                print("Paid features locked. Enter key? (y/n)")
                yn = input(">> ").strip().lower()
                if yn == "y":
                    check_key()
                else:
                    continue
            if paid_user:
                paid_feature_2()
        elif choice == "5":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid option.")
            time.sleep(1)

def party_tools():
    print_header("Party Tools")
    print("Party tools coming soon.")
    input("Press Enter to return to menu.")

def account_tools():
    print_header("Account Tools")
    print(f"Gamertag: {gamertag}")
    print(f"XUID: {xuid}")
    input("Press Enter to return to menu.")

def paid_feature_1():
    print_header("Paid Feature 1")
    print("This is a paid feature.")
    input("Press Enter to return to menu.")

def paid_feature_2():
    print_header("Paid Feature 2")
    print("This is another paid feature.")
    input("Press Enter to return to menu.")

if __name__ == "__main__":
    main_menu()
