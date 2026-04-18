import argparse
import sys
import os
sys.path.append(os.path.dirname(__file__))

from auth_manager import AuthManager
from gui import HomeNetGUI

def main():
    parser = argparse.ArgumentParser(description="HomeNet CLI/GUI")
    parser.add_argument("--gui", action="store_true", help="Launch Modern GUI")
    parser.add_argument("--cli", action="store_true", help="CLI Mode")
    parser.add_argument("--lang", default="en", choices=["en", "ar"])
    args = parser.parse_args()

    auth = AuthManager()
    if args.cli:
        u = input("Username: ")
        p = input("Password: ")
        if auth.login(u, p):
            print("[HomeNet] Logged in. Use --help for commands.")
        else:
            print("Invalid credentials.")
    elif args.gui:
        if auth.login("admin", "123456"):  # Auto-login for demo, real app shows login screen
            app = HomeNetGUI(lang=args.lang)
            app.mainloop()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()