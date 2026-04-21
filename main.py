import os
import json
from auth import authenticate, change_password
from network import block_traffic, unblock_traffic, list_hosts
from speedtest import test_speed
from database import init_db, add_rule, list_rules
from ai_assistant import generate_response

# Load translations
def load_translations(lang):
    with open(f"locale/{lang}.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Modern CLI Menu
def display_menu(translations):
    print("\n" + "=" * 40)
    print(translations["welcome"])
    print("=" * 40)
    print("1. " + translations["block_traffic"])
    print("2. " + translations["unblock_traffic"])
    print("3. " + translations["list_hosts"])
    print("4. " + translations["test_speed"])
    print("5. " + translations["list_rules"])
    print("6. " + translations["add_rule"])
    print("7. " + translations["change_password"])
    print("8. " + translations["ai_assistant"])
    print("9. " + translations["exit"])
    print("=" * 40)

def main():
    init_db()
    lang = os.getenv("LANG", "en")
    translations = load_translations(lang)

    while True:
        display_menu(translations)
        choice = input(translations["choose_option"] + ": ")

        if choice == "1":
            block_traffic()
            print(translations["traffic_blocked"])
        elif choice == "2":
            unblock_traffic()
            print(translations["traffic_unblocked"])
        elif choice == "3":
            hosts = list_hosts()
            print("\n".join(hosts) if hosts else translations["no_hosts"])
        elif choice == "4":
            speed = test_speed()
            print(speed)
        elif choice == "5":
            rules = list_rules()
            print("\n".join(rules) if rules else translations["no_rules"])
        elif choice == "6":
            rule_name = input(translations["rule_name"] + ": ")
            start_time = input(translations["start_time"] + ": ")
            end_time = input(translations["end_time"] + ": ")
            add_rule(rule_name, start_time, end_time)
            print(translations["rule_added"])
        elif choice == "7":
            change_password()
            print(translations["password_changed"])
        elif choice == "8":
            query = input(translations["ai_prompt"] + ": ")
            response = generate_response(query)
            print(translations["ai_response"] + response)
        elif choice == "9":
            print(translations["goodbye"])
            break
        else:
            print(translations["invalid_option"])

if __name__ == "__main__":
    main()