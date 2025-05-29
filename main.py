import requests
import time
import os
import sys

PAID_KEYS = {
    "EXAMPLE-KEY-1234": True,
    "ANOTHER-KEY-5678": True
}

TOKEN_VALIDITY_SECONDS = 13 * 3600

xbl_token = None
xuid = None
gamertag = None
token_auth_time = None
paid_user = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def rainbow_text(text):
    colors = [
        '\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m'
    ]
    reset = '\033[0m'
    result = ''
    for i, c in enumerate(text):
        result += colors[i % len(colors)] + c
    result += reset
    return result

def print_header(menu_title):
    clear_screen()
    print(rainbow_text(f"=== XBL Targeter ==="))
    print(rainbow_text(f"Menu: {menu_title}"))
    print("Credits: Pay2Respond | Discord: Pay2Respond | Github: Pay2Respond | TikTok: Pay2Respond")
    if xbl_token and token_auth_time:
        remaining = TOKEN_VALIDITY_SECONDS - (time.time() - token_auth_time)
        if remaining > 0:
            print(f"Authenticated: {gamertag} (XUID: {xuid}) | Token expires in: {int(remaining // 60)} minutes")
        else:
            print("Token expired - not authenticated")
    else:
        print("Not authenticated")
    print()

def input_xbl_token():
    global xbl_token, token_auth_time, xuid, gamertag
    while True:
        print_header("Please input your XBL3.0 token")
        token = input("XBL3.0 Token (must start with 'XBL3.0 x='): ").strip()
        if not token.startswith("XBL3.0 x="):
            print("Invalid token format. Try again.")
            time.sleep(1.5)
            continue

        # Validate token and fetch user data
        success = validate_xbl_token(token)
        if success:
            xbl_token = token
            token_auth_time = time.time()
            break
        else:
            print("Token validation failed. Try again.")
            time.sleep(2)

def validate_xbl_token(token):
    # Extract the token string after "XBL3.0 x="
    auth_token = token[len("XBL3.0 x="):]
    headers = {
        "Authorization": f"XBL3.0 x={auth_token}"
    }
    try:
        # Get user XUID first from XSTS token exchange endpoint
        # Since user gives token directly, use peoplehub to get user info

        # Call peoplehub to get user info - users/me
        response = requests.get("https://peoplehub.xboxlive.com/users/me/profile/settings", headers=headers, timeout=8)

        if response.status_code == 200:
            data = response.json()
            global xuid, gamertag
            # The peoplehub returns "profileUsers" list
            profile_users = data.get("profileUsers", [])
            if not profile_users:
                return False
            user_info = profile_users[0]
            xuid = user_info.get("id")
            gamertag = user_info.get("settings", [{}])[0].get("value", "Unknown")  # Might need adjustment

            # If any are missing, fail validation
            if not xuid or not gamertag:
                return False

            return True
        else:
            return False
    except Exception:
        return False

def input_paid_key():
    global paid_user
    while True:
        print_header("Paid Features")
        choice = input("Do you have a paid key? (y/n): ").strip().lower()
        if choice == "y":
            key = input("Enter paid key: ").strip()
            if PAID_KEYS.get(key):
                paid_user = True
                print("Paid features unlocked.")
                time.sleep(1)
                return
            else:
                print("Invalid key.")
                time.sleep(1)
        elif choice == "n":
            paid_user = False
            return

def main_menu():
    while True:
        print_header("Main Menu")
        print("1. Party Tools")
        print("2. Account Tools")
        if paid_user:
            print("3. Overpowered Paid Feature 1")
            print("4. Overpowered Paid Feature 2")
        print("0. Exit")
        choice = input("Select option: ").strip()
        if choice == "1":
            party_tools()
        elif choice == "2":
            account_tools()
        elif paid_user and choice == "3":
            paid_feature_1()
        elif paid_user and choice == "4":
            paid_feature_2()
        elif choice == "0":
            print("Goodbye.")
            sys.exit(0)
        else:
            print("Invalid choice. Try again.")
            time.sleep(1)

def party_tools():
    print_header("Party Tools")
    input("Party tools placeholder (press Enter to go back)")

def account_tools():
    print_header("Account Tools")
    input("Account tools placeholder (press Enter to go back)")

def paid_feature_1():
    print_header("Paid Feature 1")
    input("Overpowered paid feature 1 placeholder (press Enter to go back)")

def paid_feature_2():
    print_header("Paid Feature 2")
    input("Overpowered paid feature 2 placeholder (press Enter to go back)")

def check_token_expiry():
    if token_auth_time:
        elapsed = time.time() - token_auth_time
        if elapsed > TOKEN_VALIDITY_SECONDS:
            global xbl_token, xuid, gamertag, paid_user, token_auth_time
            xbl_token = None
            xuid = None
            gamertag = None
            paid_user = False
            token_auth_time = None
            print("\nToken expired. Please authenticate again.")
            time.sleep(2)
            return False
    return True

def main():
    while True:
        if not xbl_token:
            input_xbl_token()
            if not validate_xbl_token(xbl_token):
                print("Authentication failed. Try again.")
                continue
            input_paid_key()
        else:
            if not check_token_expiry():
                continue
        main_menu()

if __name__ == "__main__":
    main()
