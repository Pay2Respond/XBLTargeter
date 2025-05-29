import time
import threading
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich.text import Text

from xbltargeter.party import party_menu
from xbltargeter.account import account_menu
from xbltargeter.ui import render_error, render_message

console = Console()

XBL_VALIDATE_URL = "https://user.auth.xboxlive.com/user/authenticate"
XSTS_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
RELYING_PARTY = "http://auth.xboxlive.com"

XBL_TOKEN = None
GAMERTAG = None
TOKEN_EXPIRES_AT = None
TOKEN_TIMER_RUNNING = False


def validate_xbl_token(token: str):
    payload = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": f"t={token}"
        },
        "RelyingParty": RELYING_PARTY,
        "TokenType": "JWT"
    }
    try:
        r = requests.post(XBL_VALIDATE_URL, json=payload, timeout=6)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.RequestException:
        return None


def get_xsts_token(user_token: str):
    payload = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [user_token]
        },
        "RelyingParty": RELYING_PARTY,
        "TokenType": "JWT"
    }
    try:
        r = requests.post(XSTS_AUTH_URL, json=payload, timeout=6)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.RequestException:
        return None


def format_timer():
    if TOKEN_EXPIRES_AT is None:
        return "N/A"
    remaining = TOKEN_EXPIRES_AT - int(time.time())
    if remaining <= 0:
        return "Expired"
    m, s = divmod(remaining, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def start_token_timer(expiry):
    global TOKEN_EXPIRES_AT, TOKEN_TIMER_RUNNING
    TOKEN_EXPIRES_AT = expiry
    TOKEN_TIMER_RUNNING = True

    def timer_loop():
        global TOKEN_TIMER_RUNNING
        while TOKEN_TIMER_RUNNING:
            if TOKEN_EXPIRES_AT - int(time.time()) <= 0:
                TOKEN_TIMER_RUNNING = False
                break
            time.sleep(1)

    threading.Thread(target=timer_loop, daemon=True).start()


def render_header(menu_title):
    console.clear()
    title = Text("XBL Targeter", style="bold magenta")
    credits = Text("Pay2Respond (Discord | GitHub | TikTok)", style="bold cyan")
    token_text = Text.assemble(
        ("GamerTag: ", "bold green"), (GAMERTAG or "Not authenticated", "yellow"), "\n",
        ("XBL Token: ", "bold green"), (XBL_TOKEN or "None", "yellow"), "\n",
        ("Expires in: ", "bold green"), (format_timer(), "red" if format_timer() == "Expired" else "white")
    )
    console.print(Panel(Align.center(title), style="bright_blue"))
    console.print(Align.center(credits))
    console.print(Panel(token_text, style="bright_black"))
    console.print(Panel(Align.center(f"[bold underline]{menu_title}[/bold underline]"), style="bright_magenta"))


def prompt_token():
    global XBL_TOKEN, GAMERTAG, TOKEN_TIMER_RUNNING

    while True:
        render_header("Token Authorization")
        token = Prompt.ask("Enter your XBL 3.0 token")
        if not token or len(token) < 20:
            render_error("Invalid token format, try again.")
            time.sleep(2)
            continue

        validation = validate_xbl_token(token)
        if validation is None:
            render_error("Token validation failed, try again.")
            time.sleep(2)
            continue

        claims = validation.get("DisplayClaims", {}).get("xui", [{}])[0]
        gamertag = claims.get("gtg") or claims.get("gt")
        if not gamertag:
            render_error("Failed to retrieve gamer tag, try again.")
            time.sleep(2)
            continue

        expires_str = validation.get("NotAfter")
        if expires_str is None:
            render_error("Failed to get token expiration, try again.")
            time.sleep(2)
            continue

        # parse expiration ISO8601 time to epoch seconds
        try:
            from datetime import datetime
            dt = datetime.strptime(expires_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            expires_epoch = int(dt.timestamp())
        except Exception:
            render_error("Failed to parse token expiration, try again.")
            time.sleep(2)
            continue

        if expires_epoch <= int(time.time()):
            render_error("Token already expired, try again.")
            time.sleep(2)
            continue

        XBL_TOKEN = token
        GAMERTAG = gamertag
        TOKEN_TIMER_RUNNING = False
        start_token_timer(expires_epoch)
        break


def main_menu():
    while True:
        render_header("Main Menu")
        console.print("1) Party Tools")
        console.print("2) Account Tools")
        console.print("3) Exit")
        choice = Prompt.ask("Select an option", choices=["1", "2", "3"])

        if choice == "1":
            try:
                party_menu(XBL_TOKEN)
            except Exception as e:
                render_error(f"Party Tools error: {e}")
                time.sleep(2)
        elif choice == "2":
            try:
                account_menu(XBL_TOKEN)
            except Exception as e:
                render_error(f"Account Tools error: {e}")
                time.sleep(2)
        elif choice == "3":
            global TOKEN_TIMER_RUNNING
            TOKEN_TIMER_RUNNING = False
            break

        if TOKEN_EXPIRES_AT and TOKEN_EXPIRES_AT <= int(time.time()):
            render_message("Token expired. Re-authorizing...")
            time.sleep(2)
            prompt_token()


if __name__ == "__main__":
    prompt_token()
    main_menu()
