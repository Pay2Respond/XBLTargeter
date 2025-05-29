from time import time
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.live import Live
from xbltargeter.auth import validate_token, validate_license_key, get_gamer_tag
from xbltargeter.ui import render_header, render_menu, render_error, render_message
from xbltargeter.paid import is_paid_user

console = Console()

def main():
    console.clear()
    console.rule("[bold magenta]XBL Targeter[/bold magenta]")
    console.print("[green]Credits:[/] Pay2Respond\n")

    token = None
    license_key = None
    gamer_tag = None
    token_start = None
    token_expiry = 300

    while True:
        token_input = Prompt.ask("Enter your XPL 3.0 token")
        if validate_token(token_input):
            token = token_input
            gamer_tag = get_gamer_tag(token)
            token_start = time()
            break
        else:
            render_error("Invalid token, try again")

    while True:
        key_input = Prompt.ask("Enter license key (or leave blank for free mode)").strip()
        if key_input == "":
            license_key = None
            break
        if validate_license_key(key_input):
            license_key = key_input
            break
        render_error("Invalid license key")

    paid = is_paid_user(license_key)

    menu_options = {
        "1": "Party Tools",
        "2": "Account Tools",
        "3": "Advanced Party Control",
        "4": "Enhanced Account Mods",
        "5": "Help & About",
        "q": "Quit"
    }

    with Live(refresh_per_second=4, console=console) as live:
        while True:
            elapsed = int(time() - token_start)
            remaining = max(token_expiry - elapsed, 0)

            header = render_header(token, gamer_tag, remaining, paid)
            menu = render_menu(menu_options)

            live.update(Panel(header + "\n\n" + menu, border_style="bright_magenta"))

            choice = Prompt.ask("Choose option", choices=list(menu_options.keys()))

            if choice == "q":
                break
            elif choice == "1":
                from xbltargeter.party import party_menu
                party_menu(token)
            elif choice == "2":
                from xbltargeter.account import account_menu
                account_menu(token)
            elif choice == "3":
                if paid:
                    from xbltargeter.paid import advanced_party_menu
                    advanced_party_menu(token)
                else:
                    render_error("Paid feature - License required")
            elif choice == "4":
                if paid:
                    from xbltargeter.paid import enhanced_account_menu
                    enhanced_account_menu(token)
                else:
                    render_error("Paid feature - License required")
            elif choice == "5":
                from xbltargeter.ui import help_menu
                help_menu()

    console.print("Exiting XBL Targeter. Goodbye!")

if __name__ == "__main__":
    main()
