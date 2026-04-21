import os
from getpass import getpass

def authenticate():
    username = input("Username: ")
    password = getpass("Password: ")
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass = os.getenv("ADMIN_PASS", "123456")
    return username == admin_user and password == admin_pass

def change_password():
    new_password = getpass("New Password: ")
    with open(".env", "w") as f:
        f.write(f"ADMIN_USER=admin\nADMIN_PASS={new_password}\n")